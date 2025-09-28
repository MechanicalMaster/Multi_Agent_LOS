"""Data models for MSME underwriting system."""

from .base import BaseModel, TimestampedModel
from .loan_application import (
    LoanApplication,
    LoanContext,
    UploadedFile,
    ProcessingOptions,
)
from .documents import (
    DocumentClass,
    ExtractedDocument,
    ClassifiedDocuments,
    DocumentAnalysis,
    MissingDocument,
    ValidationWarning,
)
from .entity import (
    EntityProfile,
    BorrowingEntity,
    ConstitutionEligibility,
    DateOfEstablishment,
    RegisteredAddress,
)
from .kmp import (
    KMPAnalysis,
    IdentifiedKMP,
    KMPCoverageAnalysis,
    ConstitutionRequirements,
)
from .verification import (
    BureauVerificationResults,
    EntityCommercialBureau,
    KMPConsumerBureau,
    PartnershipCibilCompliance,
    EnhancedGSTAnalysis,
    PolicyComplianceAssessment,
    RiskAssessment,
    EligibilityDetermination,
)
from .financial import (
    FinancialHealthAssessment,
    TurnoverAnalysis,
    ProfitabilityRatios,
    LiquidityRatios,
    LeverageRatios,
    CashFlowAnalysis,
    LoanServicingCapacity,
)
from .banking import (
    BankingAssessment,
    AccountSummary,
    CashFlowAnalysisBank,
    AccountConduct,
    TransactionPatterns,
    FinancialIntegration,
)
from .state import (
    MSMELoanState,
    AgentContext,
    ProcessingMetadata,
    RoutingDecision,
)
from .final_report import (
    FinalReport,
    ExecutiveSummary,
    ComprehensiveBorrowerProfile,
    VerificationSummary,
    RiskAssessmentSummary,
    LoanRecommendation,
)

__all__ = [
    # Base models
    "BaseModel",
    "TimestampedModel",
    
    # Loan application
    "LoanApplication",
    "LoanContext", 
    "UploadedFile",
    "ProcessingOptions",
    
    # Documents
    "DocumentClass",
    "ExtractedDocument",
    "ClassifiedDocuments",
    "DocumentAnalysis",
    "MissingDocument",
    "ValidationWarning",
    
    # Entity
    "EntityProfile",
    "BorrowingEntity",
    "ConstitutionEligibility",
    "DateOfEstablishment",
    "RegisteredAddress",
    
    # KMP
    "KMPAnalysis",
    "IdentifiedKMP",
    "KMPCoverageAnalysis",
    "ConstitutionRequirements",
    
    # Verification
    "BureauVerificationResults",
    "EntityCommercialBureau",
    "KMPConsumerBureau",
    "PartnershipCibilCompliance",
    "EnhancedGSTAnalysis",
    "PolicyComplianceAssessment",
    "RiskAssessment",
    "EligibilityDetermination",
    
    # Financial
    "FinancialHealthAssessment",
    "TurnoverAnalysis",
    "ProfitabilityRatios",
    "LiquidityRatios",
    "LeverageRatios",
    "CashFlowAnalysis",
    "LoanServicingCapacity",
    
    # Banking
    "BankingAssessment",
    "AccountSummary",
    "CashFlowAnalysisBank",
    "AccountConduct",
    "TransactionPatterns",
    "FinancialIntegration",
    
    # State
    "MSMELoanState",
    "AgentContext",
    "ProcessingMetadata",
    "RoutingDecision",
    
    # Final report
    "FinalReport",
    "ExecutiveSummary",
    "ComprehensiveBorrowerProfile",
    "VerificationSummary",
    "RiskAssessmentSummary",
    "LoanRecommendation",
]
