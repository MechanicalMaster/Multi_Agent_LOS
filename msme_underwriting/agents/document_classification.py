"""
Agent 1: Document Classification & Extraction Agent

This agent transforms user-uploaded files into classified, structured data using 
the existing PDF/Image Processing Service and prepares data for entity analysis.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.state import MSMELoanState
from ..models.documents import (
    ClassifiedDocuments, DocumentAnalysis, ExtractedDocument, 
    DocumentClass, MissingDocument, ValidationWarning,
    PANCardData, AadhaarCardData, GSTCertificateData, 
    PartnershipDeedData, FinancialStatementData, BankStatementData
)
from ..models.base import RoutingDecision
from ..services.document_processing import DocumentProcessingService
from ..services.external_apis import FileStorageService
from .base import BaseAgent


class DocumentClassificationAgent(BaseAgent):
    """
    Agent 1: Document Classification & Extraction Agent
    
    Responsibilities:
    1. Validate loan type and file uploads
    2. Call existing PDF/Image Processing Service
    3. Parse and normalize structured data
    4. Apply MSME-specific document classification
    5. Identify financial documents (2 years audited + 1 year provisional)
    6. Detect banking documents for all declared accounts
    7. Map documents to borrower vs KMPs
    8. Analyze missing documents
    9. Assess data quality
    """
    
    def __init__(self):
        """Initialize the document classification agent."""
        super().__init__("document_classification")
        self.document_service = DocumentProcessingService()
        self.file_storage = FileStorageService()
        
        # Document classification rules
        self.msme_required_documents = {
            "borrower": ["pan_card", "gst_certificate"],
            "kmp": ["pan_card", "aadhaar_card"],
            "business": ["partnership_deed", "moa_aoa"],
            "financial": ["audited_financials_2yr", "provisional_financials_1yr", "itr_documents"],
            "banking": ["bank_statements"],
            "gst": ["gst_returns"]
        }
        
        # Financial document requirements
        self.financial_requirements = {
            "audited_financials_required": 2,
            "provisional_financials_required": 1,
            "itr_documents_required": 3
        }
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for document classification."""
        if not state.loan_application:
            raise ValueError("Loan application data is required")
        
        if not state.loan_application.uploaded_files:
            raise ValueError("No uploaded files found")
        
        # Validate loan type
        loan_type = state.loan_application.loan_context.loan_type
        if loan_type != "MSM_supply_chain":
            raise ValueError(f"Unsupported loan type: {loan_type}")
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Execute document classification and extraction."""
        loan_app = state.loan_application
        
        # Step 1: Validate loan type and files
        self._validate_loan_type(loan_app.loan_context.loan_type)
        self._validate_uploaded_files(loan_app.uploaded_files)
        
        # Step 2: Call document processing service
        processing_response = await self._call_document_processing_service(
            loan_app.uploaded_files,
            loan_app.processing_options
        )
        
        # Step 3: Parse and normalize structured data
        extracted_documents = await self._parse_processing_response(processing_response)
        
        # Step 4: Apply MSME document classification
        classified_documents = self._classify_documents_for_msme(extracted_documents)
        
        # Step 5: Identify financial documents
        self._identify_financial_documents(classified_documents)
        
        # Step 6: Identify banking documents
        self._identify_banking_documents(classified_documents)
        
        # Step 7: Map documents to entities
        self._map_documents_to_entities(classified_documents)
        
        # Step 8: Analyze missing documents
        missing_documents = self._analyze_missing_documents(classified_documents)
        
        # Step 9: Assess data quality
        validation_warnings = self._assess_data_quality(classified_documents)
        
        # Step 10: Create document analysis
        document_analysis = self._create_document_analysis(
            classified_documents, extracted_documents
        )
        
        # Determine routing decision
        routing_decision = self._determine_routing_decision(
            classified_documents, missing_documents, validation_warnings
        )
        
        return {
            "classified_documents": classified_documents,
            "document_analysis": document_analysis,
            "missing_documents": missing_documents,
            "validation_warnings": validation_warnings,
            "next_action": "proceed_to_entity_analysis",
            "routing_decision": routing_decision
        }
    
    def _validate_loan_type(self, loan_type: str) -> None:
        """Validate loan type matches MSM Supply Chain Finance requirements."""
        if loan_type != "MSM_supply_chain":
            raise ValueError(f"Invalid loan type: {loan_type}. Expected: MSM_supply_chain")
        
        self.logger.info(f"Loan type validation passed: {loan_type}")
    
    def _validate_uploaded_files(self, uploaded_files: List[Any]) -> None:
        """Validate uploaded files against business rules."""
        if not uploaded_files:
            raise ValueError("No files uploaded")
        
        total_size = sum(file.file_size for file in uploaded_files)
        max_size = 50 * 1024 * 1024  # 50MB
        
        if total_size > max_size:
            raise ValueError(f"Total file size ({total_size}) exceeds maximum ({max_size})")
        
        # Validate file types
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "application/zip"]
        for file in uploaded_files:
            if file.file_type not in allowed_types:
                raise ValueError(f"Unsupported file type: {file.file_type}")
        
        self.logger.info(f"File validation passed: {len(uploaded_files)} files, {total_size} bytes")
    
    async def _call_document_processing_service(self, uploaded_files: List[Any], 
                                              processing_options: Any) -> Dict[str, Any]:
        """Call the existing PDF/Image Processing Service."""
        try:
            self.logger.info("Calling document processing service")
            
            # Prepare request payload
            request_payload = {
                "files": [
                    {
                        "file_name": file.file_name,
                        "file_path": file.file_path,
                        "file_type": file.file_type
                    }
                    for file in uploaded_files
                ],
                "processing_options": {
                    "max_pages_per_document": processing_options.max_pages_per_document,
                    "include_raw_responses": processing_options.include_raw_responses,
                    "vision_model": processing_options.vision_model,
                    "confidence_threshold": processing_options.confidence_threshold,
                    "enable_ocr": processing_options.enable_ocr,
                    "language": processing_options.language
                }
            }
            
            # Call the service
            response = await self.document_service.process_documents(request_payload)
            self._log_api_call("document_processing_service", 0.34)  # Example cost
            
            if not response.success:
                raise ValueError(f"Document processing failed: {response.error}")
            
            self.logger.info(f"Document processing completed: {len(response.data.get('documents', []))} documents")
            return response.data
            
        except Exception as e:
            self.logger.error(f"Error calling document processing service: {str(e)}")
            raise
    
    async def _parse_processing_response(self, response: Dict[str, Any]) -> List[ExtractedDocument]:
        """Parse and normalize structured data from API response."""
        extracted_documents = []
        
        for doc_data in response.get("documents", []):
            try:
                # Determine document class
                doc_class = self._determine_document_class(doc_data)
                
                # Extract structured data based on document class
                extracted_data = self._extract_structured_data(doc_data, doc_class)
                
                # Create extracted document
                extracted_doc = ExtractedDocument(
                    file_name=doc_data.get("file_name", "unknown"),
                    document_class=doc_class,
                    extracted_data=extracted_data,
                    quality_flags=self._assess_document_quality(doc_data),
                    processing_time=doc_data.get("processing_time")
                )
                
                extracted_documents.append(extracted_doc)
                
            except Exception as e:
                self.logger.error(f"Error parsing document {doc_data.get('file_name')}: {str(e)}")
                continue
        
        self.logger.info(f"Parsed {len(extracted_documents)} documents")
        return extracted_documents
    
    def _determine_document_class(self, doc_data: Dict[str, Any]) -> DocumentClass:
        """Determine document class from processing response."""
        # This would use the classification from the document processing service
        # and map it to our DocumentClass enum
        
        doc_type = doc_data.get("document_type", "").lower()
        
        if "pan" in doc_type:
            if "individual" in doc_type:
                return DocumentClass.PAN_INDIVIDUAL
            else:
                return DocumentClass.PAN_FIRM
        elif "aadhaar" in doc_type:
            return DocumentClass.AADHAAR_INDIVIDUAL
        elif "gst" in doc_type and "certificate" in doc_type:
            return DocumentClass.GST_CERTIFICATE
        elif "partnership" in doc_type:
            return DocumentClass.PARTNERSHIP_DEED
        elif "financial" in doc_type:
            if "audited" in doc_type:
                return DocumentClass.AUDITED_FINANCIAL_STATEMENT
            else:
                return DocumentClass.PROVISIONAL_FINANCIAL_STATEMENT
        elif "bank" in doc_type:
            return DocumentClass.BANK_STATEMENT
        elif "itr" in doc_type or "income_tax" in doc_type:
            return DocumentClass.INCOME_TAX_RETURN
        elif "gst_return" in doc_type:
            return DocumentClass.GST_RETURNS
        else:
            return DocumentClass.UNKNOWN
    
    def _extract_structured_data(self, doc_data: Dict[str, Any], doc_class: DocumentClass) -> Any:
        """Extract structured data based on document class."""
        extracted_data = doc_data.get("extracted_data", {})
        confidence = doc_data.get("confidence_score", 0.0)
        
        if doc_class in [DocumentClass.PAN_FIRM, DocumentClass.PAN_INDIVIDUAL]:
            return PANCardData(
                pan_number=extracted_data.get("pan_number", ""),
                name=extracted_data.get("name"),
                entity_name=extracted_data.get("entity_name"),
                father_name=extracted_data.get("father_name"),
                date_of_birth=extracted_data.get("date_of_birth"),
                constitution_indicator=extracted_data.get("constitution_indicator"),
                address=extracted_data.get("address"),
                confidence_score=confidence
            )
        elif doc_class == DocumentClass.AADHAAR_INDIVIDUAL:
            return AadhaarCardData(
                aadhaar_number=extracted_data.get("aadhaar_number", ""),
                name=extracted_data.get("name", ""),
                address=extracted_data.get("address"),
                phone=extracted_data.get("phone"),
                date_of_birth=extracted_data.get("date_of_birth"),
                confidence_score=confidence
            )
        elif doc_class == DocumentClass.GST_CERTIFICATE:
            return GSTCertificateData(
                gst_number=extracted_data.get("gst_number", ""),
                business_name=extracted_data.get("business_name", ""),
                registration_date=extracted_data.get("registration_date"),
                address=extracted_data.get("address"),
                status=extracted_data.get("status"),
                confidence_score=confidence
            )
        elif doc_class == DocumentClass.PARTNERSHIP_DEED:
            return PartnershipDeedData(
                firm_name=extracted_data.get("firm_name", ""),
                registration_date=extracted_data.get("registration_date"),
                partners=extracted_data.get("partners", []),
                business_activity=extracted_data.get("business_activity"),
                confidence_score=confidence
            )
        elif doc_class in [DocumentClass.AUDITED_FINANCIAL_STATEMENT, DocumentClass.PROVISIONAL_FINANCIAL_STATEMENT]:
            return FinancialStatementData(
                fiscal_year=extracted_data.get("fiscal_year", 0),
                balance_sheet=extracted_data.get("balance_sheet", {}),
                profit_loss=extracted_data.get("profit_loss", {}),
                cash_flow=extracted_data.get("cash_flow"),
                auditor_name=extracted_data.get("auditor_name"),
                audit_date=extracted_data.get("audit_date"),
                confidence_score=confidence
            )
        elif doc_class == DocumentClass.BANK_STATEMENT:
            return BankStatementData(
                bank_name=extracted_data.get("bank_name", ""),
                account_number=extracted_data.get("account_number"),
                account_type=extracted_data.get("account_type"),
                period=extracted_data.get("period", ""),
                transaction_count=extracted_data.get("transaction_count", 0),
                average_balance=extracted_data.get("average_balance"),
                opening_balance=extracted_data.get("opening_balance"),
                closing_balance=extracted_data.get("closing_balance"),
                confidence_score=confidence
            )
        else:
            # Generic extracted data
            from ..models.documents import ExtractedData
            return ExtractedData(
                confidence_score=confidence,
                raw_text=extracted_data.get("raw_text"),
                structured_data=extracted_data
            )
    
    def _assess_document_quality(self, doc_data: Dict[str, Any]) -> List[str]:
        """Assess document quality and return quality flags."""
        quality_flags = []
        
        confidence = doc_data.get("confidence_score", 0.0)
        if confidence >= 0.9:
            quality_flags.append("high_confidence")
        elif confidence < 0.7:
            quality_flags.append("low_confidence")
        
        if doc_data.get("image_quality") == "clear":
            quality_flags.append("clear_image")
        elif doc_data.get("image_quality") == "blurry":
            quality_flags.append("blurry_image")
        
        if doc_data.get("text_extraction_quality") == "good":
            quality_flags.append("good_text_extraction")
        
        return quality_flags
    
    def _classify_documents_for_msme(self, extracted_documents: List[ExtractedDocument]) -> ClassifiedDocuments:
        """Apply MSME-specific document categorization."""
        classified = ClassifiedDocuments()
        
        for doc in extracted_documents:
            if doc.document_class in [DocumentClass.PAN_FIRM]:
                if "pan_cards" not in classified.borrower_documents:
                    classified.borrower_documents["pan_cards"] = []
                classified.borrower_documents["pan_cards"].append(doc)
            
            elif doc.document_class == DocumentClass.GST_CERTIFICATE:
                if "gst_certificates" not in classified.borrower_documents:
                    classified.borrower_documents["gst_certificates"] = []
                classified.borrower_documents["gst_certificates"].append(doc)
            
            elif doc.document_class == DocumentClass.PAN_INDIVIDUAL:
                if "pan_cards" not in classified.kmp_documents:
                    classified.kmp_documents["pan_cards"] = []
                classified.kmp_documents["pan_cards"].append(doc)
            
            elif doc.document_class == DocumentClass.AADHAAR_INDIVIDUAL:
                if "aadhaar_cards" not in classified.kmp_documents:
                    classified.kmp_documents["aadhaar_cards"] = []
                classified.kmp_documents["aadhaar_cards"].append(doc)
            
            elif doc.document_class == DocumentClass.PARTNERSHIP_DEED:
                if "partnership_deeds" not in classified.business_documents:
                    classified.business_documents["partnership_deeds"] = []
                classified.business_documents["partnership_deeds"].append(doc)
            
            elif doc.document_class in [DocumentClass.AUDITED_FINANCIAL_STATEMENT, DocumentClass.PROVISIONAL_FINANCIAL_STATEMENT]:
                category = "audited_financials_2yr" if doc.document_class == DocumentClass.AUDITED_FINANCIAL_STATEMENT else "provisional_financials_1yr"
                if category not in classified.financial_documents:
                    classified.financial_documents[category] = []
                classified.financial_documents[category].append(doc)
            
            elif doc.document_class == DocumentClass.INCOME_TAX_RETURN:
                if "itr_documents" not in classified.financial_documents:
                    classified.financial_documents["itr_documents"] = []
                classified.financial_documents["itr_documents"].append(doc)
            
            elif doc.document_class == DocumentClass.BANK_STATEMENT:
                if "bank_statements" not in classified.banking_documents:
                    classified.banking_documents["bank_statements"] = []
                classified.banking_documents["bank_statements"].append(doc)
            
            elif doc.document_class == DocumentClass.GST_RETURNS:
                if "gst_returns" not in classified.gst_documents:
                    classified.gst_documents["gst_returns"] = []
                classified.gst_documents["gst_returns"].append(doc)
        
        self.logger.info(f"Classified documents into {len(classified.get_all_documents())} total documents")
        return classified
    
    def _identify_financial_documents(self, classified_documents: ClassifiedDocuments) -> None:
        """Identify 2 years audited + 1 year provisional financials."""
        audited_docs = classified_documents.financial_documents.get("audited_financials_2yr", [])
        provisional_docs = classified_documents.financial_documents.get("provisional_financials_1yr", [])
        
        # Sort by fiscal year
        audited_docs.sort(key=lambda x: getattr(x.extracted_data, 'fiscal_year', 0), reverse=True)
        provisional_docs.sort(key=lambda x: getattr(x.extracted_data, 'fiscal_year', 0), reverse=True)
        
        self.logger.info(f"Identified {len(audited_docs)} audited and {len(provisional_docs)} provisional financial documents")
    
    def _identify_banking_documents(self, classified_documents: ClassifiedDocuments) -> None:
        """Identify bank statements for all declared accounts."""
        bank_statements = classified_documents.banking_documents.get("bank_statements", [])
        
        # Group by bank name
        banks = {}
        for stmt in bank_statements:
            bank_name = getattr(stmt.extracted_data, 'bank_name', 'Unknown')
            if bank_name not in banks:
                banks[bank_name] = []
            banks[bank_name].append(stmt)
        
        self.logger.info(f"Identified bank statements from {len(banks)} banks")
    
    def _map_documents_to_entities(self, classified_documents: ClassifiedDocuments) -> None:
        """Map documents to borrower vs KMPs."""
        # This is already done in the classification step
        # Additional logic could be added here for more sophisticated mapping
        
        borrower_docs = sum(len(docs) for docs in classified_documents.borrower_documents.values())
        kmp_docs = sum(len(docs) for docs in classified_documents.kmp_documents.values())
        
        self.logger.info(f"Mapped {borrower_docs} borrower documents and {kmp_docs} KMP documents")
    
    def _analyze_missing_documents(self, classified_documents: ClassifiedDocuments) -> List[MissingDocument]:
        """Analyze missing documents against MSME requirements."""
        missing_documents = []
        
        # Check borrower documents
        if not classified_documents.borrower_documents.get("pan_cards"):
            missing_documents.append(MissingDocument(
                document_type="pan_card",
                missing_for="Borrowing Entity",
                mandatory=True,
                reason="Required for entity identification"
            ))
        
        # Check financial documents
        audited_count = len(classified_documents.financial_documents.get("audited_financials_2yr", []))
        if audited_count < self.financial_requirements["audited_financials_required"]:
            missing_documents.append(MissingDocument(
                document_type="audited_financials",
                missing_for="Borrowing Entity",
                mandatory=True,
                reason=f"Required {self.financial_requirements['audited_financials_required']} years, found {audited_count}"
            ))
        
        provisional_count = len(classified_documents.financial_documents.get("provisional_financials_1yr", []))
        if provisional_count < self.financial_requirements["provisional_financials_required"]:
            missing_documents.append(MissingDocument(
                document_type="provisional_financials",
                missing_for="Borrowing Entity",
                mandatory=True,
                reason=f"Required {self.financial_requirements['provisional_financials_required']} year, found {provisional_count}"
            ))
        
        itr_count = len(classified_documents.financial_documents.get("itr_documents", []))
        if itr_count < self.financial_requirements["itr_documents_required"]:
            missing_documents.append(MissingDocument(
                document_type="itr_documents",
                missing_for="Borrowing Entity",
                mandatory=True,
                reason=f"Required {self.financial_requirements['itr_documents_required']} years, found {itr_count}"
            ))
        
        self.logger.info(f"Identified {len(missing_documents)} missing documents")
        return missing_documents
    
    def _assess_data_quality(self, classified_documents: ClassifiedDocuments) -> List[ValidationWarning]:
        """Assess data quality and flag low-quality extractions."""
        warnings = []
        
        all_docs = classified_documents.get_all_documents()
        low_confidence_docs = [
            doc for doc in all_docs 
            if hasattr(doc.extracted_data, 'confidence_score') and 
            doc.extracted_data.confidence_score < 0.9
        ]
        
        for doc in low_confidence_docs:
            warnings.append(ValidationWarning(
                type="low_confidence",
                document=doc.file_name,
                confidence=doc.extracted_data.confidence_score,
                threshold=0.9,
                recommendation="Manual review recommended",
                severity="medium"
            ))
        
        # Check average confidence
        if all_docs:
            avg_confidence = sum(
                getattr(doc.extracted_data, 'confidence_score', 0.0) 
                for doc in all_docs
            ) / len(all_docs)
            
            if avg_confidence < 0.7:
                warnings.append(ValidationWarning(
                    type="low_average_confidence",
                    confidence=avg_confidence,
                    threshold=0.7,
                    recommendation="Review document quality and consider re-upload",
                    severity="high"
                ))
        
        self.logger.info(f"Generated {len(warnings)} validation warnings")
        return warnings
    
    def _create_document_analysis(self, classified_documents: ClassifiedDocuments, 
                                extracted_documents: List[ExtractedDocument]) -> DocumentAnalysis:
        """Create document analysis summary."""
        all_docs = classified_documents.get_all_documents()
        
        # Calculate statistics
        total_pages = sum(
            getattr(doc, 'page_count', 1) for doc in extracted_documents
        )
        
        confidence_scores = [
            getattr(doc.extracted_data, 'confidence_score', 0.0) 
            for doc in all_docs
            if hasattr(doc.extracted_data, 'confidence_score')
        ]
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        classification_success_rate = len([doc for doc in all_docs if doc.document_class != DocumentClass.UNKNOWN]) / len(all_docs) if all_docs else 0.0
        
        # Financial documents coverage
        financial_coverage = {
            "audited_financials_required": self.financial_requirements["audited_financials_required"],
            "audited_financials_available": len(classified_documents.financial_documents.get("audited_financials_2yr", [])),
            "provisional_financials_required": self.financial_requirements["provisional_financials_required"],
            "provisional_financials_available": len(classified_documents.financial_documents.get("provisional_financials_1yr", [])),
            "itr_documents_required": self.financial_requirements["itr_documents_required"],
            "itr_documents_available": len(classified_documents.financial_documents.get("itr_documents", []))
        }
        
        return DocumentAnalysis(
            total_documents_processed=len(extracted_documents),
            total_pages_processed=total_pages,
            classification_success_rate=classification_success_rate,
            average_confidence_score=avg_confidence,
            financial_documents_coverage=financial_coverage
        )
    
    def _determine_routing_decision(self, classified_documents: ClassifiedDocuments,
                                  missing_documents: List[MissingDocument],
                                  validation_warnings: List[ValidationWarning]) -> RoutingDecision:
        """Determine routing decision based on processing results."""
        
        # Check if we have borrower PAN card with good confidence
        borrower_pans = classified_documents.borrower_documents.get("pan_cards", [])
        if not borrower_pans:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="No borrower PAN card found",
                conditions_met=[],
                bypass_conditions=["borrower_pan_available"]
            )
        
        # Check confidence of borrower PAN
        pan_confidence = getattr(borrower_pans[0].extracted_data, 'confidence_score', 0.0)
        if pan_confidence < 0.8:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Low confidence in borrower PAN card extraction",
                conditions_met=[],
                bypass_conditions=["high_confidence_extraction"]
            )
        
        # Check for critical missing documents
        critical_missing = [doc for doc in missing_documents if doc.mandatory]
        if len(critical_missing) > 3:  # Too many critical documents missing
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Too many critical documents missing",
                conditions_met=[],
                bypass_conditions=["sufficient_documents"]
            )
        
        # Check average confidence
        all_docs = classified_documents.get_all_documents()
        if all_docs:
            avg_confidence = sum(
                getattr(doc.extracted_data, 'confidence_score', 0.0) 
                for doc in all_docs
            ) / len(all_docs)
            
            if avg_confidence < 0.7:
                return RoutingDecision(
                    next_agent="human_review",
                    routing_reason="Average document confidence below threshold",
                    conditions_met=[],
                    bypass_conditions=["minimum_confidence"]
                )
        
        # Success route
        return RoutingDecision(
            next_agent="entity_kmp_identification",
            routing_reason="Sufficient documents available for entity analysis",
            conditions_met=[
                "borrower_pan_available",
                "sufficient_document_quality",
                "basic_documents_classified"
            ],
            bypass_conditions=[]
        )
