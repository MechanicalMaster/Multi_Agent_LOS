# Multi-Agent Loan Origination System (LOS) for MSME Underwriting

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/Powered%20by-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)

A comprehensive multi-agent system for MSME (Micro, Small & Medium Enterprise) loan underwriting using LangGraph orchestration. This system processes loan applications through a series of specialized agents that handle document classification, entity identification, verification, financial analysis, and final report generation.

## 🏗️ Architecture Overview

The system implements a 7-agent architecture orchestrated by LangGraph:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LangGraph Orchestrator                           │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌───────────┐ │
│  │   Agent 1   │────│   Agent 2   │────│   Agent 3   │────│  Agent 4  │ │
│  │  Document   │    │   Entity    │    │Verification │    │ Financial │ │
│  │ Classifier  │    │   & KMP     │    │   Agent     │    │ Analysis  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └───────────┘ │
│                                │                   │              │     │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────┐              │     │
│  │   Agent 5   │    │   Agent 6   │    │  Agent 7  │──────────────┘     │
│  │Relationship │    │Final        │    │ Banking   │                    │
│  │ Mapping     │    │Assembly     │    │ Analysis  │                    │
│  └─────────────┘    └─────────────┘    └───────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🤖 Agent Responsibilities

### Agent 1: Document Classification & Extraction
- Validates loan type and file uploads
- Integrates with existing PDF/Image Processing Service
- Applies MSME-specific document classification
- Identifies financial documents (2 years audited + 1 year provisional)
- Maps documents to borrower vs KMPs
- Assesses data quality and identifies missing documents

### Agent 2: Entity & KMP Identification
- Determines entity constitution and eligibility
- Identifies Key Management Personnel (KMP)
- Validates entity structure through external APIs
- Performs basic group company identification
- Ensures minimum KMP coverage requirements

### Agent 3: Verification & Compliance
- Validates entity and KMP information through bureau checks
- Performs enhanced GST analysis and compliance verification
- Conducts policy rule engine validation
- Calculates comprehensive risk assessment
- Determines loan eligibility

### Agent 4: Financial Analysis
- Analyzes financial statements and ratios
- Performs cash flow and profitability analysis
- Calculates debt service capacity
- Reconciles GST turnover with financial statements
- Determines loan servicing capacity

### Agent 7: Banking Analysis
- Analyzes banking behavior and transaction patterns
- Verifies cash flow consistency
- Assesses account conduct and relationships
- Integrates banking data with financial analysis

### Agent 6: Final Assembly & Report Generation
- Consolidates all processed information
- Generates comprehensive loan application report
- Creates executive summary and recommendations
- Provides structured output for underwriter review

### Agent 5: Relationship Mapping (Phase 2)
- Identifies and analyzes group companies
- Maps corporate family tree
- Assesses consolidated group exposure and risk

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL (for LangGraph checkpointing)
- Redis (for caching)
- Access to external APIs (PAN, CIBIL, GST, MCA)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd msme-loan-underwriting
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
# Create PostgreSQL database
createdb msme_underwriting

# Run migrations (if using Alembic)
alembic upgrade head
```

### Configuration

Configure the following environment variables in your `.env` file:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/msme_underwriting
REDIS_URL=redis://localhost:6379/0

# External API Keys
PAN_API_KEY=your_pan_api_key
MCA_API_KEY=your_mca_api_key
CIBIL_API_KEY=your_cibil_api_key
GST_API_KEY=your_gst_api_key

# Document Processing Service
DOCUMENT_PROCESSING_SERVICE_URL=http://localhost:8001
DOCUMENT_PROCESSING_API_KEY=your_document_service_api_key
```

## 📊 Usage

### Basic Usage

```python
from msme_underwriting import MSMELoanOrchestrator
from msme_underwriting.models import LoanApplication, LoanContext, UploadedFile

# Initialize orchestrator
orchestrator = MSMELoanOrchestrator()

# Create loan application
loan_application = LoanApplication(
    thread_id="loan_USER001_20240925_143022",
    user_id="USER001",
    loan_context=LoanContext(
        loan_type="MSM_supply_chain",
        loan_amount=5000000,
        application_timestamp=datetime.utcnow()
    ),
    uploaded_files=[
        UploadedFile(
            file_name="documents.zip",
            file_path="/uploads/USER001/loan_001/documents.zip",
            file_size=15728640,
            upload_timestamp=datetime.utcnow(),
            file_type="application/zip"
        )
    ]
)

# Process the application
final_state = await orchestrator.process_loan_application(loan_application)

# Get the final report
if final_state.final_report:
    print(f"Recommendation: {final_state.final_report.loan_recommendation.primary_recommendation}")
    print(f"Risk Grade: {final_state.final_report.executive_summary.risk_grade}")
```

### Advanced Usage with Checkpointing

```python
from langgraph.checkpoint.postgres import PostgresCheckpointer

# Initialize with checkpointing for persistence
checkpointer = PostgresCheckpointer.from_conn_string(DATABASE_URL)
orchestrator = MSMELoanOrchestrator(checkpointer=checkpointer)

# Process with ability to resume
final_state = await orchestrator.process_loan_application(loan_application)

# Resume from checkpoint if needed
resumed_state = await orchestrator.resume_processing(
    thread_id="loan_USER001_20240925_143022",
    user_input={"additional_documents": [...]}
)
```

## 🏛️ Project Structure

```
msme_underwriting/
├── __init__.py
├── orchestrator.py          # Main LangGraph orchestrator
├── agents/                  # Individual agent implementations
│   ├── __init__.py
│   ├── base.py             # Base agent class
│   ├── document_classification.py
│   ├── entity_kmp_identification.py
│   ├── verification_compliance.py
│   ├── financial_analysis.py
│   ├── banking_analysis.py
│   └── final_assembly.py
├── models/                  # Pydantic data models
│   ├── __init__.py
│   ├── base.py
│   ├── state.py            # LangGraph state model
│   ├── loan_application.py
│   ├── documents.py
│   ├── entity.py
│   ├── kmp.py
│   ├── verification.py
│   ├── financial.py
│   ├── banking.py
│   └── final_report.py
├── services/               # External service integrations
│   ├── __init__.py
│   ├── document_processing.py
│   └── external_apis.py
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py
├── utils/                  # Utility functions
│   └── __init__.py
└── api/                    # FastAPI endpoints (optional)
    └── __init__.py
```

## 🔧 Business Rules & Configuration

The system implements configurable business rules:

- **Minimum KMP Coverage**: 50% (configurable)
- **Minimum Consumer CIBIL**: 680 (configurable)
- **Maximum Commercial CMR**: 8 (configurable)
- **Eligible Constitutions**: Sole Proprietorship, Partnership, LLP, Company, HUF
- **Document Confidence Thresholds**: Minimum 70%, High confidence 90%

## 🔌 External Integrations

The system integrates with various external services:

- **Document Processing Service**: Existing PDF/Image processing API
- **PAN Validation API**: Entity and individual PAN verification
- **MCA API**: Company and director information
- **CIBIL API**: Consumer and commercial credit reports
- **GST API**: Registration, compliance, and transaction analysis
- **Banking APIs**: Account verification and transaction analysis

## 📈 Monitoring & Observability

The system includes comprehensive monitoring:

- **LangSmith Integration**: Trace all agent executions
- **Structured Logging**: Detailed logging with correlation IDs
- **Performance Metrics**: Processing time, API costs, success rates
- **Quality Metrics**: Document confidence, data completeness
- **Business Metrics**: Approval rates, processing efficiency

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=msme_underwriting

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 📋 Implementation Roadmap

### Phase 1: MVP (Agents 1, 2, 3, 4, 7, 6) - 10-12 Weeks
- ✅ Foundation setup and data models
- ✅ LangGraph orchestrator implementation
- 🔄 Agent 1: Document Classification (In Progress)
- ⏳ Agent 2: Entity & KMP Identification
- ⏳ Agent 3: Verification & Compliance
- ⏳ Agent 4: Financial Analysis
- ⏳ Agent 7: Banking Analysis
- ⏳ Agent 6: Final Assembly

### Phase 2: Enhanced Processing (Agent 5) - 4-6 Weeks
- ⏳ Agent 5: Relationship Mapping
- ⏳ Group company analysis
- ⏳ Corporate family tree mapping

### Phase 3: Production Hardening - 4-6 Weeks
- ⏳ Performance optimization
- ⏳ Security hardening
- ⏳ Monitoring and alerting
- ⏳ Load testing and scalability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the GitHub repository
- Contact the development team at dev@company.com
- Check the documentation in the `docs/` directory

## 🙏 Acknowledgments

- LangGraph team for the excellent orchestration framework
- LangChain community for the foundational tools
- All contributors and maintainers of the project
