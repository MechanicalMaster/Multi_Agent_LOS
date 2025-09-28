"""Models for final report generation."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel


class ExecutiveSummary(BaseModel):
    """Executive summary of the loan application."""
    
    application_id: str = Field(description="Unique application ID")
    borrower_name: str = Field(description="Borrower entity name")
    
    # Loan request details
    loan_request: Dict[str, Any] = Field(description="Loan request details")
    
    # Decision summary
    recommendation: str = Field(description="Final recommendation (APPROVED/CONDITIONALLY APPROVED/REJECTED)")
    risk_grade: str = Field(description="Risk grade assigned")
    processing_confidence: float = Field(description="Confidence in processing results")
    
    # Loan sizing
    recommended_loan_amount: Optional[float] = Field(default=None, description="Recommended loan amount")
    
    # Key metrics
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Key financial metrics")
    
    @property
    def is_approved(self) -> bool:
        """Check if application is approved."""
        return "APPROVED" in self.recommendation.upper()


class EntitySummary(BaseModel):
    """Summary of entity information."""
    
    legal_name: str = Field(description="Legal entity name")
    constitution: str = Field(description="Entity constitution")
    pan_number: str = Field(description="PAN number")
    gst_number: Optional[str] = Field(default=None, description="GST number")
    date_of_establishment: Optional[str] = Field(default=None, description="Date of establishment")
    registered_address: str = Field(description="Registered address")
    business_activity: Optional[str] = Field(default=None, description="Business activity")
    msm_classification: Optional[str] = Field(default=None, description="MSM classification")


class KMPSummary(BaseModel):
    """Summary of KMP information."""
    
    name: str = Field(description="KMP name")
    role: str = Field(description="Role in entity")
    shareholding: Optional[str] = Field(default=None, description="Shareholding percentage")
    pan_number: Optional[str] = Field(default=None, description="PAN number")
    cibil_score: Optional[int] = Field(default=None, description="CIBIL score")
    kyc_status: str = Field(description="KYC status")
    missing_documents: List[str] = Field(default_factory=list, description="Missing documents")
    risk_flags: str = Field(default="None", description="Risk flags")


class FinancialSummary(BaseModel):
    """Summary of financial information."""
    
    annual_turnover: str = Field(description="Annual turnover")
    growth_rate: str = Field(description="Growth rate")
    net_profit_margin: str = Field(description="Net profit margin")
    debt_equity_ratio: str = Field(description="Debt-to-equity ratio")
    working_capital: str = Field(description="Working capital")
    debt_service_capacity: str = Field(description="Debt service capacity")
    
    # Additional metrics
    current_ratio: Optional[str] = Field(default=None, description="Current ratio")
    interest_coverage: Optional[str] = Field(default=None, description="Interest coverage ratio")


class BankingSummary(BaseModel):
    """Summary of banking information."""
    
    accounts_analyzed: int = Field(description="Number of accounts analyzed")
    average_balance: str = Field(description="Average balance")
    monthly_cash_flow: str = Field(description="Monthly cash flow")
    account_conduct: str = Field(description="Account conduct rating")
    
    # Additional details
    banking_relationship_years: Optional[int] = Field(default=None, description="Banking relationship years")
    credit_facilities: Optional[str] = Field(default=None, description="Credit facilities")


class ComprehensiveBorrowerProfile(BaseModel):
    """Comprehensive borrower profile."""
    
    entity_summary: EntitySummary = Field(description="Entity summary")
    kmp_summary: List[KMPSummary] = Field(description="KMP summaries")
    financial_summary: FinancialSummary = Field(description="Financial summary")
    banking_summary: BankingSummary = Field(description="Banking summary")
    
    # Additional profile information
    business_vintage: Optional[int] = Field(default=None, description="Business vintage in years")
    industry_sector: Optional[str] = Field(default=None, description="Industry sector")
    geographic_presence: Optional[List[str]] = Field(default=None, description="Geographic presence")


class ScoreSummary(BaseModel):
    """Summary of scores."""
    
    cmr_score: Optional[int] = Field(default=None, description="CMR score")
    grade: Optional[str] = Field(default=None, description="Commercial grade")
    status: str = Field(description="Status")


class CibilSummary(BaseModel):
    """Summary of CIBIL scores."""
    
    average_cibil: Optional[int] = Field(default=None, description="Average CIBIL score")
    lowest_score: Optional[int] = Field(default=None, description="Lowest score")
    all_above_threshold: bool = Field(description="All above threshold")


class ComplianceStatus(BaseModel):
    """Compliance status summary."""
    
    gst_compliance: str = Field(description="GST compliance status")
    pan_validation: str = Field(description="PAN validation status")
    documentation: str = Field(description="Documentation status")


class VerificationSummary(BaseModel):
    """Summary of verification results."""
    
    entity_commercial_score: ScoreSummary = Field(description="Entity commercial score")
    kmp_consumer_scores: CibilSummary = Field(description="KMP consumer scores")
    compliance_status: ComplianceStatus = Field(description="Compliance status")


class RiskAssessmentSummary(BaseModel):
    """Summary of risk assessment."""
    
    overall_risk_score: float = Field(description="Overall risk score")
    risk_category: str = Field(description="Risk category")
    risk_grade: str = Field(description="Risk grade")
    
    key_strengths: List[str] = Field(description="Key strengths")
    areas_of_concern: List[str] = Field(description="Areas of concern")
    recommended_mitigations: List[str] = Field(description="Recommended mitigations")


class ProposedTerms(BaseModel):
    """Proposed loan terms."""
    
    loan_amount: float = Field(description="Proposed loan amount")
    tenure: str = Field(description="Proposed tenure")
    interest_rate: str = Field(description="Proposed interest rate")
    emi: str = Field(description="Estimated EMI")
    dscr: float = Field(description="Debt service coverage ratio")
    
    # Additional terms
    security: Optional[str] = Field(default=None, description="Security requirements")
    guarantees: Optional[str] = Field(default=None, description="Guarantee requirements")
    covenants: Optional[List[str]] = Field(default=None, description="Loan covenants")


class LoanRecommendation(BaseModel):
    """Final loan recommendation."""
    
    primary_recommendation: str = Field(description="Primary recommendation")
    confidence_level: str = Field(description="Confidence level")
    recommended_loan_amount: float = Field(description="Recommended loan amount")
    
    suggested_conditions: List[str] = Field(description="Suggested conditions")
    proposed_terms: ProposedTerms = Field(description="Proposed terms")
    
    estimated_processing_timeline: str = Field(description="Estimated processing timeline")
    next_steps: List[str] = Field(description="Next steps")
    
    # Risk mitigation
    risk_mitigation_measures: Optional[List[str]] = Field(
        default=None,
        description="Risk mitigation measures"
    )
    
    # Monitoring requirements
    monitoring_requirements: Optional[List[str]] = Field(
        default=None,
        description="Ongoing monitoring requirements"
    )


class ProcessingSummary(BaseModel):
    """Summary of processing workflow."""
    
    total_processing_time: float = Field(description="Total processing time in seconds")
    agents_executed: List[str] = Field(description="List of agents executed")
    total_api_calls: int = Field(description="Total API calls made")
    total_api_cost: float = Field(description="Total API cost")
    
    # Processing efficiency
    processing_efficiency: Optional[str] = Field(default=None, description="Processing efficiency rating")
    automation_percentage: Optional[float] = Field(default=None, description="Automation percentage")


class QualityMetrics(BaseModel):
    """Quality metrics for the processing."""
    
    document_confidence_average: float = Field(description="Average document confidence")
    data_completeness_score: float = Field(description="Data completeness score")
    cross_validation_score: float = Field(description="Cross-validation score")
    
    # Quality flags
    quality_flags: List[str] = Field(default_factory=list, description="Quality flags")
    manual_review_required: bool = Field(description="Whether manual review is required")


class FinalReport(BaseModel):
    """Complete final report for loan application."""
    
    # Report metadata
    report_id: str = Field(description="Unique report ID")
    thread_id: str = Field(description="Thread ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time")
    report_version: str = Field(default="1.0", description="Report version")
    
    # Core sections
    executive_summary: ExecutiveSummary = Field(description="Executive summary")
    comprehensive_borrower_profile: ComprehensiveBorrowerProfile = Field(
        description="Comprehensive borrower profile"
    )
    verification_summary: VerificationSummary = Field(description="Verification summary")
    risk_assessment_summary: RiskAssessmentSummary = Field(description="Risk assessment summary")
    loan_recommendation: LoanRecommendation = Field(description="Loan recommendation")
    
    # Processing information
    processing_summary: ProcessingSummary = Field(description="Processing summary")
    quality_metrics: QualityMetrics = Field(description="Quality metrics")
    
    # Supporting data
    supporting_documents: List[str] = Field(default_factory=list, description="Supporting documents")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    
    # Compliance and audit
    compliance_checklist: Dict[str, bool] = Field(
        default_factory=dict,
        description="Compliance checklist"
    )
    audit_trail: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Audit trail of processing steps"
    )
    
    # Warnings and disclaimers
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    disclaimers: List[str] = Field(default_factory=list, description="Disclaimers")
    
    # Additional sections for comprehensive reporting
    market_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Market analysis")
    industry_comparison: Optional[Dict[str, Any]] = Field(default=None, description="Industry comparison")
    regulatory_compliance: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Regulatory compliance details"
    )
    
    def add_audit_entry(self, agent: str, action: str, timestamp: datetime, details: Dict[str, Any]) -> None:
        """Add an audit trail entry."""
        entry = {
            "agent": agent,
            "action": action,
            "timestamp": timestamp,
            "details": details
        }
        self.audit_trail.append(entry)
    
    def add_supporting_document(self, document_name: str) -> None:
        """Add a supporting document."""
        if document_name not in self.supporting_documents:
            self.supporting_documents.append(document_name)
    
    def add_data_source(self, source: str) -> None:
        """Add a data source."""
        if source not in self.data_sources:
            self.data_sources.append(source)
    
    def mark_compliance_item(self, item: str, status: bool) -> None:
        """Mark a compliance checklist item."""
        self.compliance_checklist[item] = status
    
    @property
    def is_approved(self) -> bool:
        """Check if the loan is approved."""
        return self.executive_summary.is_approved
    
    @property
    def requires_manual_review(self) -> bool:
        """Check if manual review is required."""
        return self.quality_metrics.manual_review_required
    
    @property
    def processing_time_minutes(self) -> float:
        """Get processing time in minutes."""
        return self.processing_summary.total_processing_time / 60.0
    
    def get_recommendation_summary(self) -> str:
        """Get a brief recommendation summary."""
        return f"{self.loan_recommendation.primary_recommendation} - {self.loan_recommendation.confidence_level}"
