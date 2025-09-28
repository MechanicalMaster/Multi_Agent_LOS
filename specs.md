# Complete MSME Loan Processing Agent Architecture: Implementation Specifications (UPDATED)

## **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LangGraph Orchestrator                           │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌───────────┐ │
│  │   Agent 1   │    │   Agent 2   │    │   Agent 3   │    │  Agent 4  │ │
│  │  Document   │────│   Entity    │────│Verification │────│ Financial │ │
│  │ Classifier  │    │   & KMP     │    │   Agent     │    │ Analysis  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └───────────┘ │
│                                │                   │              │     │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────┐              │     │
│  │   Agent 5   │    │   Agent 6   │    │  Agent 7  │              │     │
│  │Relationship │    │Final        │    │ Banking   │──────────────┘     │
│  │ Mapping     │    │Assembly     │    │ Analysis  │                    │
│  └─────────────┘    └───────────┘    └───────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
           │                   │                   │              │
           ▼                   ▼                   ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│           PDF/Image Processing Service (Existing FastAPI)              │
│                     POST /process-documents                             │
└─────────────────────────────────────────────────────────────────────────┘
           │                   │                   │              │
           ▼                   ▼                   ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     External APIs Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ PAN/MCA     │  │ Bureau APIs │  │ GST/Banking │  │ Financial   │    │
│  │ APIs        │  │ (CIBIL)     │  │ APIs        │  │ APIs        │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## **Agent 1: Document Classification & Extraction Agent**

### **Purpose**
Transform user-uploaded files into classified, structured data using the existing PDF/Image Processing Service and prepare data for entity analysis.

### **Call Condition**
- **Triggered by**: New loan application initiation
- **Prerequisites**: User file upload completed
- **State Check**: `current_step == "start"` or `current_step == "document_reupload"`

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "user_id": "USER001",
  "loan_context": {
    "loan_type": "MSM_supply_chain",
    "loan_amount": 5000000,
    "application_timestamp": "2024-09-25T14:30:22Z"
  },
  "uploaded_files": [
    {
      "file_name": "documents.zip",
      "file_path": "/uploads/USER001/loan_001/documents.zip",
      "file_size": 15728640,
      "upload_timestamp": "2024-09-25T14:30:22Z",
      "file_type": "application/zip"
    }
  ],
  "processing_options": {
    "max_pages_per_document": 50,
    "include_raw_responses": false,
    "vision_model": "gpt-4o"
  }
}
```

### **Processing Logic**
1. **Loan Type Validation**: Validate loan type matches MSM Supply Chain Finance requirements
2. **File Validation**: Check file types, sizes, formats against business rules
3. **Document Service Integration**: Call existing `/process-documents` endpoint
4. **Response Parsing**: Extract and normalize structured data from API response
5. **MSME Document Classification**: Apply business-specific document categorization
6. **Financial Document Identification**: Identify 2 years audited + 1 year provisional financials
7. **Banking Document Detection**: Identify bank statements for all declared accounts
8. **Entity-Document Mapping**: Identify which documents belong to borrower vs KMPs
9. **Missing Document Analysis**: Compare available documents against MSME requirements
10. **Data Quality Assessment**: Evaluate confidence scores and flag low-quality extractions

### **External Service Calls**
- **PDF/Image Processing Service**: `POST /process-documents` with uploaded files
- **File Storage Service**: Document storage and retrieval

### **Expected Output**
```json
{
  "agent_name": "document_classification",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "processing_metadata": {
    "start_time": "2024-09-25T14:30:25Z",
    "end_time": "2024-09-25T14:32:58Z",
    "total_processing_time": 153.2,
    "api_calls_made": 12,
    "total_api_cost": 0.34
  },
  "loan_type_validation": {
    "requested_loan_type": "MSM_supply_chain",
    "is_eligible": true,
    "validation_checks": [
      {"check": "msm_loan_type", "status": "passed"},
      {"check": "supply_chain_finance", "status": "passed"}
    ]
  },
  "classified_documents": {
    "borrower_documents": {
      "pan_cards": [
        {
          "file_name": "entity_pan.pdf",
          "document_class": "PAN_FIRM",
          "extracted_data": {
            "pan_number": "ABCDE1234F",
            "entity_name": "ABC Enterprises",
            "constitution_indicator": "D",
            "address": "123 Business Street, Mumbai",
            "confidence_score": 0.95
          },
          "quality_flags": ["high_confidence", "clear_image"]
        }
      ],
      "gst_certificates": [
        {
          "file_name": "gst_cert.pdf", 
          "document_class": "GST_CERTIFICATE",
          "extracted_data": {
            "gst_number": "09ABCDE1234F1Z5",
            "business_name": "ABC Enterprises",
            "registration_date": "2019-04-15",
            "address": "123 Business Street, Mumbai",
            "status": "Active",
            "confidence_score": 0.89
          }
        }
      ]
    },
    "kmp_documents": {
      "pan_cards": [
        {
          "file_name": "partner1_pan.pdf",
          "document_class": "PAN_INDIVIDUAL", 
          "extracted_data": {
            "pan_number": "XYZPQ5678R",
            "name": "John Doe",
            "father_name": "Robert Doe",
            "date_of_birth": "1985-03-15",
            "confidence_score": 0.92
          }
        }
      ],
      "aadhaar_cards": [
        {
          "file_name": "partner1_aadhaar.pdf",
          "document_class": "AADHAAR_INDIVIDUAL",
          "extracted_data": {
            "aadhaar_number": "1234-5678-9012", 
            "name": "John Doe",
            "address": "456 Residential Area, Mumbai",
            "phone": "9876543210",
            "confidence_score": 0.88
          }
        }
      ]
    },
    "business_documents": {
      "partnership_deeds": [
        {
          "file_name": "partnership_deed.pdf",
          "document_class": "PARTNERSHIP_DEED",
          "extracted_data": {
            "firm_name": "ABC Enterprises",
            "registration_date": "2019-02-20",
            "partners": [
              {"name": "John Doe", "share": "30%"},
              {"name": "Jane Smith", "share": "35%"},
              {"name": "Mike Johnson", "share": "20%"},
              {"name": "Sarah Wilson", "share": "15%"}
            ],
            "confidence_score": 0.87
          }
        }
      ]
    },
    "financial_documents": {
      "audited_financials_2yr": [
        {
          "file_name": "financials_2023.pdf",
          "document_class": "AUDITED_FINANCIAL_STATEMENT",
          "fiscal_year": 2023,
          "extracted_data": {
            "balance_sheet": {"status": "extracted", "confidence": 0.85},
            "profit_loss": {"status": "extracted", "confidence": 0.83},
            "cash_flow": {"status": "extracted", "confidence": 0.82}
          }
        },
        {
          "file_name": "financials_2022.pdf",
          "document_class": "AUDITED_FINANCIAL_STATEMENT", 
          "fiscal_year": 2022,
          "extracted_data": {
            "balance_sheet": {"status": "extracted", "confidence": 0.86},
            "profit_loss": {"status": "extracted", "confidence": 0.84},
            "cash_flow": {"status": "extracted", "confidence": 0.81}
          }
        }
      ],
      "provisional_financials_1yr": [
        {
          "file_name": "financials_2024_provisional.pdf",
          "document_class": "PROVISIONAL_FINANCIAL_STATEMENT",
          "fiscal_year": 2024,
          "extracted_data": {
            "balance_sheet": {"status": "extracted", "confidence": 0.78},
            "profit_loss": {"status": "extracted", "confidence": 0.76}
          }
        }
      ],
      "itr_documents": [
        {
          "file_name": "itr_2023.pdf",
          "document_class": "INCOME_TAX_RETURN",
          "assessment_year": "2023-24",
          "extracted_data": {
            "itr_form": "ITR-3",
            "schedules_present": ["3AA", "3CA"],
            "income_computation": {"status": "extracted", "confidence": 0.88}
          }
        }
      ]
    },
    "banking_documents": {
      "bank_statements": [
        {
          "file_name": "bank_statement_hdfc.pdf",
          "document_class": "BANK_STATEMENT",
          "bank_name": "HDFC Bank",
          "account_type": "Current Account",
          "period": "2023-04-01 to 2024-03-31",
          "extracted_data": {
            "transaction_count": 2456,
            "average_balance": 1250000,
            "confidence_score": 0.91
          }
        }
      ]
    },
    "gst_documents": {
      "gst_returns": [
        {
          "file_name": "gst_returns_2023.zip",
          "document_class": "GST_RETURNS",
          "period": "2023-2024",
          "extracted_data": {
            "return_forms": ["GSTR-1", "GSTR-3B"],
            "filing_frequency": "Monthly",
            "confidence_score": 0.89
          }
        }
      ]
    }
  },
  "document_analysis": {
    "total_documents_processed": 15,
    "total_pages_processed": 87,
    "classification_success_rate": 0.93,
    "average_confidence_score": 0.91,
    "financial_documents_coverage": {
      "audited_financials_required": 2,
      "audited_financials_available": 2,
      "provisional_financials_required": 1,
      "provisional_financials_available": 1,
      "itr_documents_required": 3,
      "itr_documents_available": 1
    }
  },
  "missing_documents": [
    {
      "document_type": "aadhaar_card",
      "missing_for": "Jane Smith (Partner)",
      "mandatory": true,
      "reason": "Required for KMP KYC completion"
    },
    {
      "document_type": "udyam_registration",
      "missing_for": "ABC Enterprises",
      "mandatory": false, 
      "reason": "Helps establish MSM status"
    },
    {
      "document_type": "itr_documents",
      "missing_for": "2022-23, 2021-22 assessment years",
      "mandatory": true,
      "reason": "Required for 2-year financial analysis"
    }
  ],
  "validation_warnings": [
    {
      "type": "low_confidence",
      "document": "partner1_aadhaar.pdf", 
      "confidence": 0.88,
      "threshold": 0.90,
      "recommendation": "Manual review recommended"
    }
  ],
  "next_action": "proceed_to_entity_analysis",
  "routing_decision": {
    "next_agent": "entity_kmp_identification",
    "routing_reason": "Sufficient documents available for entity analysis",
    "bypass_conditions": []
  }
}
```

### **Routing Conditions**
- **Success Route**: If borrower PAN card available and confidence >0.8 → Route to Agent 2
- **Missing Docs Route**: If critical documents missing → Route to Human Interface
- **Quality Issues Route**: If average confidence <0.7 → Route to Human Review
- **Error Route**: If API failures or processing errors → Route to Error Handler

---

## **Agent 2: Entity & KMP Identification Agent (ENHANCED)**

### **Purpose**
Determine entity constitution, identify required Key Management Personnel, collect their KYC information, validate entity structure, and perform basic group company identification.

### **Call Condition**
- **Triggered by**: Agent 1 completion with sufficient document classification
- **Prerequisites**: Borrower PAN card available, basic entity documents identified
- **State Check**: `current_step == "entity_analysis"` and `classified_documents.borrower_documents.pan_cards` exists

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "agent_context": {
    "previous_agent": "document_classification",
    "trigger_reason": "documents_classified_successfully", 
    "processing_timestamp": "2024-09-25T14:32:58Z"
  },
  "classified_documents": {
    "borrower_documents": {...},
    "kmp_documents": {...},
    "business_documents": {...},
    "financial_documents": {...},
    "banking_documents": {...},
    "gst_documents": {...}
  },
  "loan_context": {
    "loan_type": "MSM_supply_chain",
    "loan_amount": 5000000
  },
  "business_rules": {
    "minimum_kmp_coverage": 0.5,
    "required_documents_by_constitution": {
      "partnership": ["partnership_deed", "pan_cards", "aadhaar_cards"],
      "company": ["moa_aoa", "pan_cards", "aadhaar_cards"],
      "sole_proprietorship": ["pan_card", "aadhaar_card"]
    },
    "eligible_constitutions": ["sole_proprietorship", "partnership", "llp", "company", "huf"]
  }
}
```

### **Processing Logic**
1. **Primary Entity Identification**: Extract and validate borrowing entity details
2. **Constitution Eligibility Verification**: Validate against 5 eligible constitution types
3. **KMP Requirements Definition**: Define required personnel based on constitution
4. **Document-KMP Matching**: Match available documents to identified individuals
5. **Basic Group Company Identification**: Analyze ITR income sources for group entities
6. **API Validation**: Verify PAN numbers and fetch additional entity data
7. **Coverage Analysis**: Calculate KMP coverage percentage
8. **Cross-Document Validation**: Ensure consistency across documents
9. **Missing KYC Identification**: Identify gaps in required documentation
10. **Establishment Date Determination**: Use document hierarchy for date validation

### **External API Calls**
- **PAN Validation API**: Verify all PAN numbers and extract verified names
- **MCA API**: For companies/LLPs, fetch director/partner details and shareholding
- **Name Matching Service**: Cross-reference names across multiple documents
- **Address Validation API**: Standardize and validate addresses

### **Expected Output**
```json
{
  "agent_name": "entity_kmp_identification",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "processing_metadata": {
    "start_time": "2024-09-25T14:32:59Z",
    "end_time": "2024-09-25T14:35:42Z",
    "total_processing_time": 163.1,
    "api_calls_made": 8,
    "total_api_cost": 0.12
  },
  "entity_profile": {
    "borrowing_entity": {
      "pan_number": "ABCDE1234F",
      "entity_name": "ABC Enterprises",
      "constitution": "partnership",
      "constitution_source": "pan_4th_letter_D",
      "constitution_eligibility": {
        "eligible_types": ["sole_proprietorship", "partnership", "llp", "company", "huf"],
        "detected_type": "partnership",
        "is_eligible": true,
        "validation_checks": [
          {"check": "pan_4th_character", "status": "passed", "value": "D"},
          {"check": "eligible_constitution", "status": "passed"}
        ]
      },
      "api_verified": true,
      "verified_name": "ABC ENTERPRISES",
      "gst_number": "09ABCDE1234F1Z5",
      "udyam_number": null,
      "date_of_establishment": {
        "determined_date": "2019-02-20",
        "source_document": "partnership_deed",
        "hierarchy_used": ["partnership_deed", "pan_card", "gst_certificate"],
        "confidence": 0.95
      },
      "registered_address": {
        "line1": "123 Business Street",
        "line2": "",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "standardized": true
      },
      "business_activity": "Trading and Services",
      "entity_validation_score": 0.94
    }
  },
  "kmp_analysis": {
    "constitution_requirements": {
      "entity_type": "partnership",
      "minimum_partners_required": 2,
      "maximum_partners_allowed": 20,
      "minimum_coverage_required": 0.5
    },
    "identified_kmps": [
      {
        "kmp_id": "KMP001",
        "name": "John Doe",
        "role": "partner",
        "pan_number": "XYZPQ5678R", 
        "aadhaar_number": "1234-5678-9012",
        "shareholding_percentage": 30,
        "documents_available": ["pan", "aadhaar"],
        "api_verified": true,
        "verified_name": "JOHN DOE",
        "address": {
          "line1": "456 Residential Area",
          "city": "Mumbai", 
          "state": "Maharashtra",
          "pincode": "400002"
        },
        "phone_number": "9876543210",
        "kyc_completeness": "complete",
        "risk_flags": []
      },
      {
        "kmp_id": "KMP002",
        "name": "Jane Smith",
        "role": "partner", 
        "shareholding_percentage": 35,
        "documents_available": ["identified_in_deed"],
        "api_verified": false,
        "kyc_completeness": "incomplete",
        "missing_documents": ["pan_card", "aadhaar_card"]
      }
    ],
    "kmp_coverage_analysis": {
      "total_partners_identified": 4,
      "partners_with_complete_kyc": 1,
      "partners_with_partial_kyc": 1,
      "total_shareholding_covered": 65,
      "minimum_coverage_met": true,
      "coverage_percentage": 0.65
    }
  },
  "basic_group_identification": {
    "analysis_performed": true,
    "data_sources_used": ["itr_documents", "partnership_deed"],
    "identified_related_entities": [
      {
        "entity_name": "XYZ Trading Co.",
        "relation_type": "kmp_affiliation",
        "related_kmp": "John Doe",
        "kmp_role": "proprietor",
        "source_document": "itr_2023.pdf",
        "income_source": "business_income",
        "confidence_level": "medium"
      }
    ],
    "group_mapping_required": true,
    "additional_documents_needed": ["xyz_trading_pan", "xyz_trading_gst"]
  },
  "cross_validation_results": {
    "entity_name_consistency": "passed",
    "address_consistency": "passed_with_variations",
    "pan_cross_reference": "passed",
    "partnership_deed_alignment": "passed",
    "discrepancies": [
      {
        "type": "address_variation",
        "details": "Entity address varies slightly between PAN and GST certificate",
        "severity": "low"
      }
    ]
  },
  "missing_requirements": [
    {
      "requirement_type": "kmp_kyc",
      "missing_for": "Jane Smith",
      "required_documents": ["pan_card", "aadhaar_card"],
      "shareholding_impact": 35,
      "mandatory": true,
      "business_justification": "Required for >50% partner coverage"
    },
    {
      "requirement_type": "kmp_kyc", 
      "missing_for": "Mike Johnson",
      "required_documents": ["pan_card", "aadhaar_card"],
      "shareholding_impact": 20,
      "mandatory": false,
      "business_justification": "Optional - coverage already >50%"
    }
  ],
  "next_action": "proceed_to_verification",
  "routing_decision": {
    "next_agent": "verification_compliance",
    "routing_reason": "Minimum KMP coverage achieved, entity profile complete",
    "conditions_met": [
      "entity_identified",
      "minimum_coverage_achieved", 
      "primary_kmp_validated",
      "constitution_eligible"
    ]
  }
}
```

### **Routing Conditions**
- **Success Route**: If minimum KMP coverage (50%) met and constitution eligible → Route to Agent 3
- **Insufficient Coverage Route**: If <50% KMP coverage → Route to Human Interface for document collection
- **API Validation Failure Route**: If critical API validations fail → Route to Manual Review
- **Constitution Issues Route**: If ineligible constitution type → Route to Rejection Handler

---

## **Agent 3: Verification & Compliance Agent (ENHANCED)**

### **Purpose**
Validate entity and KMP information through bureau checks, ensure regulatory compliance, perform enhanced GST analysis, and assess overall loan eligibility.

### **Call Condition**
- **Triggered by**: Agent 2 completion with minimum KMP coverage
- **Prerequisites**: Entity profile complete, minimum 50% KMP coverage achieved
- **State Check**: `current_step == "verification"` and `kmp_analysis.coverage_percentage >= 0.5`

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "agent_context": {
    "previous_agent": "entity_kmp_identification",
    "trigger_reason": "minimum_coverage_achieved",
    "processing_timestamp": "2024-09-25T14:35:42Z"
  },
  "entity_profile": {...},
  "kmp_analysis": {...},
  "classified_documents": {
    "gst_documents": {...},
    "financial_documents": {...}
  },
  "compliance_requirements": {
    "bureau_score_thresholds": {
      "minimum_consumer_cibil": 680,
      "maximum_commercial_cmr": 8,
      "minimum_commercial_score": 1,
      "partnership_cibil_requirements": "50%_partners_above_680"
    },
    "mandatory_checks": [
      "entity_commercial_bureau",
      "kmp_consumer_bureau", 
      "gst_compliance_check",
      "pan_validation_check",
      "gst_transaction_analysis"
    ],
    "risk_assessment_weights": {
      "bureau_scores": 0.4,
      "document_quality": 0.2,
      "kmp_coverage": 0.2,
      "compliance_status": 0.2
    },
    "gst_analysis_requirements": {
      "turnover_verification": true,
      "filing_regularity_check": true,
      "multi_state_analysis": true,
      "revenue_reconciliation": true
    }
  }
}
```

### **Processing Logic**
1. **Bureau Score Retrieval**: Fetch commercial and consumer bureau scores for all entities
2. **Partnership CIBIL Validation**: Ensure 50% of partners meet 680+ score requirement
3. **Enhanced GST Analysis**: Perform detailed GST return processing and turnover analysis
4. **Compliance Threshold Validation**: Check all scores against business policy thresholds
5. **GST Compliance Verification**: Validate GST registration status and filing compliance
6. **Revenue Reconciliation**: Cross-verify GST turnover with financial statements
7. **Cross-Reference Identity Verification**: Validate identity consistency across all sources
8. **Risk Score Calculation**: Compute weighted risk assessment based on all factors
9. **Policy Rule Engine**: Apply comprehensive business rules for eligibility determination
10. **Exception Handling**: Identify cases requiring manual underwriter review

### **External API Calls**
- **Consumer Bureau API**: CIBIL scores and credit history for all identified KMPs
- **Commercial Bureau API**: Commercial credit score and history for borrowing entity
- **GST Compliance API**: Registration status, return filing history, and compliance score
- **GST Transaction API**: Detailed return analysis for turnover verification
- **PAN Status API**: Validate PAN status and any deactivation issues
- **Identity Cross-Reference API**: Validate identity consistency across databases

### **Expected Output**
```json
{
  "agent_name": "verification_compliance",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "processing_metadata": {
    "start_time": "2024-09-25T14:35:43Z",
    "end_time": "2024-09-25T14:38:21Z", 
    "total_processing_time": 158.4,
    "api_calls_made": 12,
    "total_api_cost": 0.34
  },
  "bureau_verification_results": {
    "entity_commercial_bureau": {
      "bureau_provider": "CIBIL",
      "cmr_score": 6,
      "commercial_score": "BB",
      "score_date": "2024-09-20",
      "credit_history_months": 36,
      "total_exposure": 12500000,
      "overdue_amount": 0,
      "status": "pass",
      "risk_indicators": []
    },
    "kmp_consumer_bureaus": [
      {
        "kmp_id": "KMP001",
        "name": "John Doe",
        "pan_number": "XYZPQ5678R",
        "cibil_score": 742,
        "score_date": "2024-09-18",
        "credit_history_months": 84,
        "total_accounts": 8,
        "active_accounts": 6,
        "overdue_accounts": 0,
        "total_exposure": 850000,
        "status": "pass",
        "risk_flags": []
      }
    ],
    "partnership_cibil_compliance": {
      "requirement": "50%_partners_above_680",
      "total_partners": 4,
      "partners_with_scores": 1,
      "partners_above_threshold": 1,
      "compliance_status": "incomplete_data",
      "additional_kmps_needed": 1
    }
  },
  "enhanced_gst_analysis": {
    "gst_compliance": {
      "gst_number": "09ABCDE1234F1Z5",
      "registration_status": "Active",
      "registration_date": "2019-04-15",
      "last_return_filed": "2024-08-20",
      "filing_frequency": "Monthly",
      "compliance_score": 85,
      "pending_returns": 0,
      "status": "pass"
    },
    "gst_transaction_analysis": {
      "analysis_period": "2023-2024",
      "total_turnover": 125000000,
      "average_monthly_turnover": 10416667,
      "turnover_growth_rate": 0.15,
      "major_states": ["Maharashtra", "Gujarat", "Karnataka"],
      "filing_regularity": "consistent",
      "tax_payment_pattern": "timely",
      "revenue_reconciliation": {
        "gst_turnover": 125000000,
        "financial_statement_turnover": 118000000,
        "variance_percentage": 5.9,
        "reconciliation_status": "within_tolerance",
        "tolerance_threshold": 10.0
      }
    }
  },
  "pan_validation": {
    "entity_pan": "ABCDE1234F",
    "pan_status": "Valid",
    "name_match": "Exact",
    "status": "pass"
  },
  "policy_compliance_assessment": {
    "bureau_score_compliance": {
      "consumer_cibil_check": {
        "required": ">=680",
        "achieved": [742],
        "status": "pass"
      },
      "commercial_cmr_check": {
        "required": "1-8",
        "achieved": 6,
        "status": "pass"
      },
      "partnership_cibil_check": {
        "required": "50%_partners_above_680",
        "achieved": "25%_with_data",
        "status": "requires_additional_data"
      }
    },
    "coverage_compliance": {
      "kmp_coverage_check": {
        "required": ">=50%",
        "achieved": "65%",
        "status": "pass"
      }
    },
    "documentation_compliance": {
      "critical_documents_check": {
        "required": ["entity_pan", "kmp_kyc"],
        "status": "pass"
      }
    },
    "gst_compliance_check": {
      "filing_regularity": "pass",
      "turnover_verification": "pass",
      "revenue_reconciliation": "pass"
    }
  },
  "risk_assessment": {
    "overall_risk_score": 0.32,
    "risk_category": "low",
    "risk_grade": "A2",
    "contributing_factors": [
      {
        "factor": "Strong CIBIL scores",
        "impact": "positive",
        "weight": 0.3
      },
      {
        "factor": "Good commercial bureau rating",
        "impact": "positive", 
        "weight": 0.25
      },
      {
        "factor": "Excellent GST compliance",
        "impact": "positive",
        "weight": 0.2
      },
      {
        "factor": "Incomplete partner CIBIL data",
        "impact": "negative",
        "weight": 0.15
      }
    ],
    "mitigating_factors": [],
    "risk_mitigation_required": false
  },
  "eligibility_determination": {
    "overall_eligibility": "conditionally_approved",
    "approval_confidence": 0.85,
    "conditions": [
      "Complete KMP CIBIL score submission for remaining partners",
      "Provide missing ITR documents for complete financial analysis"
    ],
    "recommendations": [
      "Proceed with financial analysis for loan structuring",
      "Collect additional partner bureau reports"
    ]
  },
  "validation_warnings": [
    {
      "type": "incomplete_kmp_bureau_data",
      "message": "Only 25% of partners have bureau scores available",
      "severity": "medium",
      "impact": "requires_manual_review"
    },
    {
      "type": "incomplete_financial_documents",
      "message": "Missing ITR documents for 2022-23, 2021-22 assessment years",
      "severity": "high",
      "impact": "financial_analysis_limited"
    }
  ],
  "next_action": "proceed_to_financial_analysis",
  "routing_decision": {
    "next_agent": "financial_analysis",
    "routing_reason": "Basic compliance checks passed, financial analysis required",
    "conditions_met": [
      "bureau_scores_passed",
      "compliance_verified",
      "risk_assessment_completed"
    ]
  }
}
```

### **Routing Conditions**
- **Approval Route**: If all compliance checks pass → Route to Agent 4 (Financial Analysis)
- **Conditional Approval Route**: If minor issues but overall eligible → Route to Agent 4 with conditions
- **Manual Review Route**: If bureau scores borderline or mixed results → Route to Human Interface
- **Rejection Route**: If critical compliance failures → Route to Rejection Handler

---

## **Agent 4: Financial Analysis Agent (MOVED TO MVP)**

### **Purpose**
Analyze financial statements, bank statements, GST returns, and ITR documents to assess financial health and loan servicing capacity.

### **Call Condition**
- **Triggered by**: Agent 3 completion with conditional or full approval
- **Prerequisites**: Verification passed, financial documents available
- **State Check**: `current_step == "financial_analysis"` and `eligibility_determination.overall_eligibility != "rejected"`

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "agent_context": {
    "previous_agent": "verification_compliance",
    "trigger_reason": "comprehensive_analysis_required"
  },
  "classified_documents": {
    "financial_documents": {...},
    "banking_documents": {...},
    "gst_documents": {...}
  },
  "entity_profile": {...},
  "enhanced_gst_analysis": {...},
  "analysis_requirements": {
    "analysis_period": "24_months",
    "required_ratios": ["current_ratio", "debt_equity_ratio", "turnover_growth", "profitability_margins"],
    "cash_flow_analysis": true,
    "working_capital_assessment": true,
    "debt_service_capacity": true,
    "financial_statement_reconciliation": true
  }
}
```

### **Processing Logic**
1. **Financial Statement Processing**: Extract and analyze 2 years audited + 1 year provisional financials
2. **Ratio Analysis**: Calculate key financial ratios and trends
3. **Bank Statement Integration**: Correlate banking data with financial statements
4. **GST-Financial Reconciliation**: Cross-verify turnover between GST and financials
5. **Cash Flow Analysis**: Assess operating, investing, and financing cash flows
6. **Debt Service Capacity**: Calculate debt service coverage ratio (DSCR)
7. **Working Capital Assessment**: Analyze working capital requirements and cycle
8. **Profitability Analysis**: Evaluate margins and return metrics
9. **Growth Trend Analysis**: Identify revenue and profit growth patterns
10. **Loan Servicing Capacity**: Determine maximum sustainable EMI

### **External API Calls**
- **Financial Data Extraction API**: Advanced financial statement parsing
- **Banking Analytics API**: Transaction pattern analysis
- **Ratio Analysis Engine**: Industry benchmark comparisons
- **Cash Flow Modeling API**: Projection and sensitivity analysis

### **Expected Output**
```json
{
  "agent_name": "financial_analysis",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "processing_metadata": {
    "start_time": "2024-09-25T14:38:22Z",
    "end_time": "2024-09-25T14:41:15Z",
    "total_processing_time": 173.2,
    "api_calls_made": 9,
    "total_api_cost": 0.28
  },
  "financial_health_assessment": {
    "turnover_analysis": {
      "annual_turnover_2023": 118000000,
      "annual_turnover_2022": 102000000,
      "growth_rate": 15.7,
      "industry_benchmark": 12.0,
      "assessment": "above_average"
    },
    "profitability_ratios": {
      "net_profit_margin_2023": 8.2,
      "net_profit_margin_2022": 7.8,
      "gross_profit_margin_2023": 22.5,
      "operating_profit_margin_2023": 12.3,
      "trend": "improving",
      "industry_comparison": "favorable"
    },
    "liquidity_ratios": {
      "current_ratio_2023": 1.8,
      "quick_ratio_2023": 1.2,
      "working_capital": 8500000,
      "assessment": "adequate"
    },
    "leverage_ratios": {
      "debt_equity_ratio_2023": 1.2,
      "debt_service_coverage_ratio": 2.1,
      "interest_coverage_ratio": 4.8,
      "assessment": "manageable"
    },
    "cash_flow_analysis": {
      "operating_cash_flow": 12500000,
      "investing_cash_flow": -4500000,
      "financing_cash_flow": -3000000,
      "free_cash_flow": 8000000,
      "cash_flow_stability": "stable"
    }
  },
  "banking_integration_analysis": {
    "account_analysis": {
      "total_accounts": 3,
      "average_monthly_balance": 1250000,
      "transaction_volume": 2456,
      "account_conduct": "satisfactory"
    },
    "cash_flow_patterns": {
      "monthly_inflows": 9850000,
      "monthly_outflows": 8720000,
      "net_monthly_surplus": 1130000,
      "seasonality_detected": "moderate"
    }
  },
  "gst_financial_reconciliation": {
    "reconciliation_status": "verified",
    "gst_reported_turnover": 125000000,
    "financial_statement_turnover": 118000000,
    "variance_explanation": "timing_differences_export_sales",
    "adjusted_turnover": 121500000
  },
  "loan_servicing_capacity": {
    "monthly_cash_flow": 1130000,
    "debt_service_capacity": 450000,
    "recommended_emi": 380000,
    "debt_service_coverage_ratio": 2.1,
    "maximum_sustainable_loan": 4500000,
    "requested_loan_servicing": {
      "requested_amount": 5000000,
      "estimated_emi": 422000,
      "dscr_at_requested": 1.98,
      "servicing_comfort": "adequate"
    }
  },
  "risk_assessment_enhancement": {
    "financial_risk_score": 0.18,
    "key_strengths": [
      "Strong revenue growth trajectory",
      "Healthy profitability margins",
      "Adequate liquidity position",
      "Stable cash flow generation"
    ],
    "concerns": [
      "Moderate leverage position",
      "Seasonal business patterns"
    ],
    "mitigation_factors": [
      "Strong debt service coverage",
      "Consistent banking conduct"
    ]
  },
  "recommendations": {
    "loan_amount_adjustment": {
      "recommended_amount": 4500000,
      "rationale": "Optimal balance of funding needs and servicing capacity",
      "confidence": 0.88
    },
    "terms_suggestions": {
      "tenure": "36 months",
      "interest_rate": "12.5%",
      "moratorium_period": "3 months"
    }
  },
  "next_action": "proceed_to_banking_analysis",
  "routing_decision": {
    "next_agent": "banking_analysis",
    "routing_reason": "Financial analysis complete, banking validation required",
    "conditions_met": [
      "financial_statements_analyzed",
      "cash_flow_assessed",
      "servicing_capacity_calculated"
    ]
  }
}
```

### **Routing Conditions**
- **Success Route**: If financial health satisfactory → Route to Agent 7 (Banking Analysis)
- **Marginal Route**: If borderline financials → Route to Human Review with recommendations
- **Poor Financials Route**: If inadequate servicing capacity → Route to Rejection Handler
- **Data Quality Issues**: If insufficient financial data → Route to Document Collection

---

## **Agent 7: Banking Analysis Agent (NEW - MVP)**

### **Purpose**
Comprehensive analysis of banking behavior, transaction patterns, cash flow verification, and account conduct assessment.

### **Call Condition**
- **Triggered by**: Agent 4 completion with financial analysis
- **Prerequisites**: Bank statements available and processed
- **State Check**: `current_step == "banking_analysis"` and `classified_documents.banking_documents` exists

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "agent_context": {
    "previous_agent": "financial_analysis",
    "trigger_reason": "banking_validation_required"
  },
  "classified_documents": {
    "banking_documents": {...}
  },
  "financial_analysis": {...},
  "analysis_requirements": {
    "analysis_period": "12_months",
    "transaction_analysis": true,
    "cash_flow_verification": true,
    "account_conduct_assessment": true,
    "pattern_analysis": true
  }
}
```

### **Processing Logic**
1. **Bank Statement Processing**: Extract all transactions and account details
2. **Cash Flow Verification**: Correlate with financial statement cash flows
3. **Transaction Pattern Analysis**: Identify business patterns and anomalies
4. **Account Conduct Assessment**: Evaluate banking behavior and relationships
5. **Balance Analysis**: Assess average balances and volatility
6. **Bounce Analysis**: Check for cheque returns or payment failures
7. **Integration with Financials**: Verify consistency with reported numbers
8. **Risk Pattern Detection**: Identify suspicious or risky transaction patterns

### **Expected Output**
```json
{
  "agent_name": "banking_analysis",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "banking_assessment": {
    "account_summary": {
      "total_accounts_analyzed": 3,
      "current_accounts": 2,
      "od_cc_accounts": 1,
      "analysis_period": "12 months"
    },
    "cash_flow_analysis": {
      "average_monthly_credits": 9850000,
      "average_monthly_debits": 8720000,
      "net_monthly_surplus": 1130000,
      "cash_flow_consistency": "high",
      "seasonality_adjusted_flow": 1050000
    },
    "account_conduct": {
      "average_balance": 1250000,
      "minimum_balance": 450000,
      "od_utilization": 35.2,
      "bounce_incidents": 2,
      "conduct_rating": "satisfactory"
    },
    "transaction_patterns": {
      "primary_business_pattern": "wholesale_trading",
      "major_counterparties": ["Supplier A", "Customer B", "Customer C"],
      "transaction_regularity": "consistent",
      "anomalies_detected": 3,
      "anomaly_severity": "low"
    },
    "financial_integration": {
      "reported_turnover_vs_banking": "consistent",
      "cash_flow_reconciliation": "verified",
      "discrepancies": "minimal"
    }
  },
  "next_action": "proceed_to_final_assembly"
}
```

---

## **Agent 5: Relationship Mapping Agent (Phase 2)**

### **Purpose**
Identify and analyze group companies, related entities, and corporate family tree to assess overall group exposure and risk.

### **Call Condition**
- **Triggered by**: Agent 4 completion or when group companies detected in KMP income sources
- **Prerequisites**: KMP ITR analysis showing income from other entities
- **State Check**: `group_companies_detected == true` or `comprehensive_due_diligence_required == true`

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "kmp_income_analysis": {...},
  "detected_related_entities": [...],
  "relationship_mapping_requirements": {
    "minimum_shareholding_threshold": 0.1,
    "include_indirect_holdings": true,
    "analyze_group_financials": true
  }
}
```

### **Expected Output**
```json
{
  "agent_name": "relationship_mapping",
  "corporate_family_tree": {...},
  "group_exposure_analysis": {...},
  "consolidated_risk_assessment": {...},
  "next_action": "proceed_to_final_assembly"
}
```

---

## **Agent 6: Final Assembly & Report Generation Agent (UPDATED)**

### **Purpose**
Consolidate all processed information into a comprehensive loan application report for human underwriter review and decision-making.

### **Call Condition**
- **Triggered by**: Agent 7 completion (Banking Analysis) in MVP
- **Prerequisites**: All mandatory validations completed, eligibility determined
- **State Check**: `banking_analysis_completed == true` and `eligibility != "rejected"`

### **Input Specifications**
```json
{
  "thread_id": "loan_USER001_20240925_143022",
  "consolidated_data": {
    "classified_documents": {...},
    "entity_profile": {...},
    "kmp_analysis": {...},
    "verification_results": {...},
    "financial_analysis": {...},
    "banking_analysis": {...},
    "relationship_mapping": {...}  // Optional - Phase 2
  },
  "report_configuration": {
    "report_type": "comprehensive",
    "include_supporting_documents": true,
    "generate_executive_summary": true,
    "output_formats": ["structured_json", "pdf_report", "excel_workbook"]
  }
}
```

### **Processing Logic**
1. **Data Consolidation**: Merge and validate all agent outputs for consistency
2. **Executive Summary Generation**: Create high-level summary for quick underwriter review
3. **Risk Profile Compilation**: Aggregate all risk factors and mitigation strategies
4. **Financial Capacity Integration**: Incorporate banking and financial analysis
5. **Document Package Assembly**: Organize all supporting documents with clear labeling
6. **Recommendation Formulation**: Generate clear recommendation with supporting rationale
7. **Quality Assurance**: Final validation of data completeness and accuracy
8. **Multi-Format Report Generation**: Create reports in multiple formats for different stakeholders

### **Expected Output**
```json
{
  "agent_name": "final_assembly",
  "processing_status": "completed",
  "thread_id": "loan_USER001_20240925_143022",
  "processing_metadata": {
    "start_time": "2024-09-25T14:41:16Z",
    "end_time": "2024-09-25T14:43:15Z",
    "total_processing_time": 119.8,
    "total_workflow_time": 768.3,
    "total_api_cost": 1.08
  },
  "executive_summary": {
    "application_id": "LOAN_2024_001",
    "borrower_name": "ABC Enterprises",
    "loan_request": {
      "amount": 5000000,
      "type": "MSM_supply_chain",
      "purpose": "Working capital financing"
    },
    "recommendation": "CONDITIONALLY APPROVED",
    "risk_grade": "A2",
    "processing_confidence": 0.85,
    "recommended_loan_amount": 4500000
  },
  "comprehensive_borrower_profile": {
    "entity_summary": {
      "legal_name": "ABC Enterprises", 
      "constitution": "Partnership",
      "pan_number": "ABCDE1234F",
      "gst_number": "09ABCDE1234F1Z5",
      "date_of_establishment": "2019-02-20",
      "registered_address": "123 Business Street, Mumbai, Maharashtra 400001",
      "business_activity": "Trading and Services",
      "msm_classification": "Small Enterprise"
    },
    "kmp_summary": [
      {
        "name": "John Doe",
        "role": "Partner",
        "shareholding": "30%",
        "pan_number": "XYZPQ5678R",
        "cibil_score": 742,
        "kyc_status": "Complete",
        "risk_flags": "None"
      },
      {
        "name": "Jane Smith",
        "role": "Partner", 
        "shareholding": "35%",
        "kyc_status": "Incomplete",
        "missing_documents": ["PAN Card", "Aadhaar Card"]
      }
    ],
    "financial_summary": {
      "annual_turnover": "₹11.8 Cr (2023)",
      "growth_rate": "15.7%",
      "net_profit_margin": "8.2%",
      "debt_equity_ratio": "1.2",
      "working_capital": "₹85 Lakhs",
      "debt_service_capacity": "₹4.5 Lakhs/month"
    },
    "banking_summary": {
      "accounts_analyzed": 3,
      "average_balance": "₹12.5 Lakhs",
      "monthly_cash_flow": "₹11.3 Lakhs",
      "account_conduct": "Satisfactory"
    }
  },
  "verification_summary": {
    "entity_commercial_score": {
      "cmr_score": 6,
      "grade": "BB",
      "status": "Pass"
    },
    "kmp_consumer_scores": {
      "average_cibil": 742,
      "lowest_score": 742,
      "all_above_threshold": true
    },
    "compliance_status": {
      "gst_compliance": "Active & Compliant",
      "pan_validation": "Valid",
      "documentation": "Adequate"
    }
  },
  "risk_assessment_summary": {
    "overall_risk_score": 0.28,
    "risk_category": "Low",
    "risk_grade": "A2",
    "key_strengths": [
      "Strong CIBIL scores across KMPs",
      "Excellent GST compliance history",
      "Good commercial bureau rating",
      "Adequate partner coverage (65%)",
      "Healthy financial performance",
      "Stable banking conduct"
    ],
    "areas_of_concern": [
      "Incomplete KMP documentation (35% shareholding)",
      "Incomplete partner CIBIL data",
      "Moderate leverage position"
    ],
    "recommended_mitigations": [
      "Collect remaining partner KYC documents",
      "Obtain bureau reports for additional partners",
      "Monitor leverage ratios during loan tenure"
    ]
  },
  "loan_recommendation": {
    "primary_recommendation": "APPROVED WITH CONDITIONS",
    "confidence_level": "High (85%)",
    "recommended_loan_amount": 4500000,
    "suggested_conditions": [
      "Complete KMP documentation for 35% shareholding partners",
      "Submit bureau reports for remaining partners",
      "Standard security and documentation",
      "Regular financial monitoring during loan period"
    ],
    "proposed_terms": {
      "loan_amount": 4500000,
      "tenure": "36 months",
      "interest_rate": "12.5%",
      "emi": "₹150,000",
      "dscr": 2.1
    },
    "estimated_processing_timeline": "3-5 business days",
    "next_steps": [
      "Underwriter review of conditions",
      "Collection of pending documents",
      "Final credit committee approval"
    ]
  },
  // ... [rest of the output remains similar with enhanced financial and banking sections]
}
```

### **Routing Conditions**
- **Completion Route**: Workflow complete → Store final report and notify human underwriter
- **Enhancement Route**: If group companies identified → Route to Agent 5 (Relationship Mapping)
- **Reprocessing Route**: If critical errors found → Route back to appropriate agent
- **Approval Route**: If auto-approval criteria met → Route to Loan Processing System

---

## **Updated Implementation Roadmap**

### **Phase 1: MVP (Agents 1, 2, 3, 4, 7, 6) - 10-12 Weeks**

#### **Week 1-2: Foundation Setup**
- LangGraph environment setup with PostgreSQL persistence
- Basic state management and thread configuration
- Integration with existing PDF/Image Processing Service
- Core data models and validation schemas

#### **Week 3-4: Agent 1 Development**
- Document classification logic implementation
- API integration with existing document service
- Financial and banking document identification
- Quality assessment and confidence scoring

#### **Week 5-6: Agent 2 Development**
- Entity constitution determination logic
- KMP identification and matching algorithms
- Basic group company identification
- External API integrations (PAN, MCA)

#### **Week 7-8: Agent 3 Development**
- Bureau score integration (CIBIL, Commercial)
- Enhanced GST analysis and transaction processing
- Compliance checking engine
- Risk assessment algorithms

#### **Week 9-10: Agent 4 & 7 Development**
- Financial statement analysis engine
- Banking statement processing algorithms
- Cash flow and ratio analysis
- Loan servicing capacity assessment

#### **Week 11-12: Agent 6 & Integration**
- Final report generation system with financial integration
- Multi-format output generation
- End-to-end workflow testing
- Human interface development

### **Phase 2: Enhanced Processing (Agent 5) - 4-6 Weeks**

#### **Week 13-16: Agent 5 Development**
- Group company identification logic
- Relationship mapping algorithms
- Consolidated risk assessment
- Corporate structure analysis

### **Phase 3: Production Hardening - 4-6 Weeks**

#### **Week 17-20: Production Readiness**
- Performance optimization and caching
- Security hardening and data protection
- Monitoring and alerting systems
- Load testing and scalability validation

#### **Week 21-22: Deployment & Training**
- Production deployment and configuration
- User training and documentation
- Go-live support and monitoring
- Performance tuning and optimization

---
