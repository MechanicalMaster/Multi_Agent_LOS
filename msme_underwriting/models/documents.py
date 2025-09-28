"""Models for document classification and extraction."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel


class DocumentClass(str, Enum):
    """Enumeration of document classes."""
    
    # PAN Cards
    PAN_FIRM = "PAN_FIRM"
    PAN_INDIVIDUAL = "PAN_INDIVIDUAL"
    
    # Identity Documents
    AADHAAR_INDIVIDUAL = "AADHAAR_INDIVIDUAL"
    
    # Business Registration
    GST_CERTIFICATE = "GST_CERTIFICATE"
    PARTNERSHIP_DEED = "PARTNERSHIP_DEED"
    MOA_AOA = "MOA_AOA"
    UDYAM_REGISTRATION = "UDYAM_REGISTRATION"
    
    # Financial Documents
    AUDITED_FINANCIAL_STATEMENT = "AUDITED_FINANCIAL_STATEMENT"
    PROVISIONAL_FINANCIAL_STATEMENT = "PROVISIONAL_FINANCIAL_STATEMENT"
    INCOME_TAX_RETURN = "INCOME_TAX_RETURN"
    
    # Banking Documents
    BANK_STATEMENT = "BANK_STATEMENT"
    
    # GST Documents
    GST_RETURNS = "GST_RETURNS"
    
    # Other
    UNKNOWN = "UNKNOWN"


class ExtractedData(BaseModel):
    """Base class for extracted document data."""
    
    confidence_score: float = Field(description="Confidence score of extraction")
    raw_text: Optional[str] = Field(default=None, description="Raw extracted text")
    structured_data: Dict[str, Any] = Field(default_factory=dict, description="Structured extracted data")


class PANCardData(ExtractedData):
    """Extracted data from PAN card."""
    
    pan_number: str = Field(description="PAN number")
    name: Optional[str] = Field(default=None, description="Name on PAN card")
    entity_name: Optional[str] = Field(default=None, description="Entity name (for firm PAN)")
    father_name: Optional[str] = Field(default=None, description="Father's name (for individual PAN)")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")
    constitution_indicator: Optional[str] = Field(default=None, description="4th character indicating constitution")
    address: Optional[str] = Field(default=None, description="Address on PAN card")


class AadhaarCardData(ExtractedData):
    """Extracted data from Aadhaar card."""
    
    aadhaar_number: str = Field(description="Aadhaar number")
    name: str = Field(description="Name on Aadhaar card")
    address: Optional[str] = Field(default=None, description="Address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")


class GSTCertificateData(ExtractedData):
    """Extracted data from GST certificate."""
    
    gst_number: str = Field(description="GST number")
    business_name: str = Field(description="Business name")
    registration_date: Optional[str] = Field(default=None, description="Registration date")
    address: Optional[str] = Field(default=None, description="Registered address")
    status: Optional[str] = Field(default=None, description="GST status")


class PartnershipDeedData(ExtractedData):
    """Extracted data from partnership deed."""
    
    firm_name: str = Field(description="Firm name")
    registration_date: Optional[str] = Field(default=None, description="Registration date")
    partners: List[Dict[str, str]] = Field(default_factory=list, description="List of partners with shares")
    business_activity: Optional[str] = Field(default=None, description="Business activity")


class FinancialStatementData(ExtractedData):
    """Extracted data from financial statements."""
    
    fiscal_year: int = Field(description="Fiscal year")
    balance_sheet: Dict[str, Any] = Field(default_factory=dict, description="Balance sheet data")
    profit_loss: Dict[str, Any] = Field(default_factory=dict, description="P&L statement data")
    cash_flow: Optional[Dict[str, Any]] = Field(default=None, description="Cash flow statement data")
    auditor_name: Optional[str] = Field(default=None, description="Auditor name")
    audit_date: Optional[str] = Field(default=None, description="Audit date")


class BankStatementData(ExtractedData):
    """Extracted data from bank statement."""
    
    bank_name: str = Field(description="Bank name")
    account_number: Optional[str] = Field(default=None, description="Account number (masked)")
    account_type: Optional[str] = Field(default=None, description="Account type")
    period: str = Field(description="Statement period")
    transaction_count: int = Field(description="Number of transactions")
    average_balance: Optional[float] = Field(default=None, description="Average balance")
    opening_balance: Optional[float] = Field(default=None, description="Opening balance")
    closing_balance: Optional[float] = Field(default=None, description="Closing balance")


class ExtractedDocument(BaseModel):
    """A document with extracted data."""
    
    file_name: str = Field(description="Original file name")
    document_class: DocumentClass = Field(description="Classified document type")
    extracted_data: ExtractedData = Field(description="Extracted structured data")
    quality_flags: List[str] = Field(default_factory=list, description="Quality assessment flags")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    
    # Additional metadata
    fiscal_year: Optional[int] = Field(default=None, description="Fiscal year (for financial docs)")
    assessment_year: Optional[str] = Field(default=None, description="Assessment year (for ITR)")
    period: Optional[str] = Field(default=None, description="Period covered by document")


class DocumentCategory(BaseModel):
    """A category of documents."""
    
    category_name: str = Field(description="Name of the document category")
    documents: List[ExtractedDocument] = Field(description="Documents in this category")
    
    def get_by_class(self, doc_class: DocumentClass) -> List[ExtractedDocument]:
        """Get documents by class."""
        return [doc for doc in self.documents if doc.document_class == doc_class]


class ClassifiedDocuments(BaseModel):
    """All classified documents organized by entity."""
    
    borrower_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict, 
        description="Documents belonging to borrowing entity"
    )
    kmp_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict,
        description="Documents belonging to KMPs"
    )
    business_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict,
        description="Business registration and legal documents"
    )
    financial_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict,
        description="Financial statements and tax documents"
    )
    banking_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict,
        description="Bank statements and banking documents"
    )
    gst_documents: Dict[str, List[ExtractedDocument]] = Field(
        default_factory=dict,
        description="GST returns and related documents"
    )
    
    def get_all_documents(self) -> List[ExtractedDocument]:
        """Get all documents as a flat list."""
        all_docs = []
        for category in [
            self.borrower_documents,
            self.kmp_documents, 
            self.business_documents,
            self.financial_documents,
            self.banking_documents,
            self.gst_documents
        ]:
            for doc_list in category.values():
                all_docs.extend(doc_list)
        return all_docs
    
    def get_documents_by_class(self, doc_class: DocumentClass) -> List[ExtractedDocument]:
        """Get all documents of a specific class."""
        return [doc for doc in self.get_all_documents() if doc.document_class == doc_class]


class DocumentAnalysis(BaseModel):
    """Analysis of document processing results."""
    
    total_documents_processed: int = Field(description="Total number of documents processed")
    total_pages_processed: int = Field(description="Total number of pages processed")
    classification_success_rate: float = Field(description="Classification success rate")
    average_confidence_score: float = Field(description="Average confidence score")
    
    financial_documents_coverage: Dict[str, int] = Field(
        default_factory=dict,
        description="Coverage analysis for financial documents"
    )
    
    processing_statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional processing statistics"
    )


class MissingDocument(BaseModel):
    """Information about a missing required document."""
    
    document_type: str = Field(description="Type of missing document")
    missing_for: str = Field(description="Entity/person the document is missing for")
    mandatory: bool = Field(description="Whether this document is mandatory")
    reason: str = Field(description="Reason why this document is required")
    alternative_documents: List[str] = Field(
        default_factory=list,
        description="Alternative documents that could substitute"
    )


class ValidationWarning(BaseModel):
    """Warning about document validation issues."""
    
    type: str = Field(description="Type of validation warning")
    document: Optional[str] = Field(default=None, description="Document that triggered the warning")
    confidence: Optional[float] = Field(default=None, description="Confidence score if applicable")
    threshold: Optional[float] = Field(default=None, description="Threshold that was not met")
    recommendation: str = Field(description="Recommended action")
    severity: str = Field(default="medium", description="Severity level")
    impact: Optional[str] = Field(default=None, description="Impact of this warning")
