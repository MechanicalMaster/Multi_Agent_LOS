"""Models for verification and compliance analysis."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel, ValidationResult


class EntityCommercialBureau(BaseModel):
    """Commercial bureau results for entity."""
    
    bureau_provider: str = Field(description="Bureau provider (e.g., CIBIL)")
    cmr_score: Optional[int] = Field(default=None, description="CMR score")
    commercial_score: Optional[str] = Field(default=None, description="Commercial score grade")
    score_date: Optional[str] = Field(default=None, description="Score date")
    credit_history_months: Optional[int] = Field(default=None, description="Credit history in months")
    total_exposure: Optional[float] = Field(default=None, description="Total credit exposure")
    overdue_amount: Optional[float] = Field(default=None, description="Overdue amount")
    status: str = Field(description="Verification status (pass/fail)")
    risk_indicators: List[str] = Field(default_factory=list, description="Risk indicators")
    
    # Detailed bureau data
    account_summary: Optional[Dict[str, Any]] = Field(default=None, description="Account summary")
    payment_history: Optional[Dict[str, Any]] = Field(default=None, description="Payment history")
    enquiry_summary: Optional[Dict[str, Any]] = Field(default=None, description="Enquiry summary")
    
    @property
    def is_within_cmr_limit(self) -> bool:
        """Check if CMR score is within acceptable limits."""
        if self.cmr_score is None:
            return False
        return 1 <= self.cmr_score <= 8
    
    @property
    def has_overdue_amounts(self) -> bool:
        """Check if there are overdue amounts."""
        return self.overdue_amount is not None and self.overdue_amount > 0


class KMPConsumerBureau(BaseModel):
    """Consumer bureau results for KMP."""
    
    kmp_id: str = Field(description="KMP identifier")
    name: str = Field(description="KMP name")
    pan_number: str = Field(description="PAN number")
    
    # CIBIL details
    cibil_score: Optional[int] = Field(default=None, description="CIBIL score")
    score_date: Optional[str] = Field(default=None, description="Score date")
    credit_history_months: Optional[int] = Field(default=None, description="Credit history in months")
    
    # Account details
    total_accounts: Optional[int] = Field(default=None, description="Total accounts")
    active_accounts: Optional[int] = Field(default=None, description="Active accounts")
    overdue_accounts: Optional[int] = Field(default=None, description="Overdue accounts")
    closed_accounts: Optional[int] = Field(default=None, description="Closed accounts")
    
    # Exposure details
    total_exposure: Optional[float] = Field(default=None, description="Total exposure")
    current_balance: Optional[float] = Field(default=None, description="Current balance")
    overdue_amount: Optional[float] = Field(default=None, description="Overdue amount")
    
    # Status and flags
    status: str = Field(description="Verification status (pass/fail)")
    risk_flags: List[str] = Field(default_factory=list, description="Risk flags")
    
    # Detailed data
    account_details: List[Dict[str, Any]] = Field(default_factory=list, description="Account details")
    enquiry_details: List[Dict[str, Any]] = Field(default_factory=list, description="Enquiry details")
    
    @property
    def meets_cibil_threshold(self) -> bool:
        """Check if CIBIL score meets threshold (680+)."""
        return self.cibil_score is not None and self.cibil_score >= 680
    
    @property
    def has_recent_enquiries(self) -> bool:
        """Check if there are recent credit enquiries."""
        return len(self.enquiry_details) > 0


class PartnershipCibilCompliance(BaseModel):
    """CIBIL compliance for partnership entities."""
    
    requirement: str = Field(description="Compliance requirement")
    total_partners: int = Field(description="Total number of partners")
    partners_with_scores: int = Field(description="Partners with CIBIL scores")
    partners_above_threshold: int = Field(description="Partners above CIBIL threshold")
    compliance_status: str = Field(description="Compliance status")
    additional_kmps_needed: int = Field(default=0, description="Additional KMPs needed for compliance")
    
    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage."""
        if self.total_partners == 0:
            return 0.0
        return self.partners_above_threshold / self.total_partners
    
    @property
    def meets_50_percent_rule(self) -> bool:
        """Check if 50% of partners meet CIBIL threshold."""
        return self.compliance_percentage >= 0.5


class GSTCompliance(BaseModel):
    """GST compliance details."""
    
    gst_number: str = Field(description="GST number")
    registration_status: str = Field(description="Registration status")
    registration_date: Optional[str] = Field(default=None, description="Registration date")
    last_return_filed: Optional[str] = Field(default=None, description="Last return filed date")
    filing_frequency: Optional[str] = Field(default=None, description="Filing frequency")
    compliance_score: Optional[int] = Field(default=None, description="Compliance score")
    pending_returns: int = Field(default=0, description="Number of pending returns")
    status: str = Field(description="Overall compliance status")
    
    # Detailed compliance data
    return_filing_history: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Return filing history"
    )
    tax_payment_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tax payment history"
    )
    
    @property
    def is_active(self) -> bool:
        """Check if GST registration is active."""
        return self.registration_status.lower() == "active"
    
    @property
    def has_pending_returns(self) -> bool:
        """Check if there are pending returns."""
        return self.pending_returns > 0


class GSTTransactionAnalysis(BaseModel):
    """GST transaction analysis results."""
    
    analysis_period: str = Field(description="Analysis period")
    total_turnover: float = Field(description="Total turnover from GST")
    average_monthly_turnover: float = Field(description="Average monthly turnover")
    turnover_growth_rate: Optional[float] = Field(default=None, description="Turnover growth rate")
    
    # Geographic analysis
    major_states: List[str] = Field(description="Major states of operation")
    interstate_percentage: Optional[float] = Field(default=None, description="Interstate transaction percentage")
    
    # Compliance patterns
    filing_regularity: str = Field(description="Filing regularity assessment")
    tax_payment_pattern: str = Field(description="Tax payment pattern")
    
    # Revenue reconciliation
    revenue_reconciliation: Dict[str, Any] = Field(description="Revenue reconciliation details")
    
    @property
    def shows_consistent_growth(self) -> bool:
        """Check if turnover shows consistent growth."""
        return self.turnover_growth_rate is not None and self.turnover_growth_rate > 0
    
    @property
    def reconciliation_within_tolerance(self) -> bool:
        """Check if revenue reconciliation is within tolerance."""
        reconciliation = self.revenue_reconciliation
        return reconciliation.get("reconciliation_status") == "within_tolerance"


class EnhancedGSTAnalysis(BaseModel):
    """Enhanced GST analysis results."""
    
    gst_compliance: GSTCompliance = Field(description="GST compliance details")
    gst_transaction_analysis: GSTTransactionAnalysis = Field(description="Transaction analysis")
    
    # Additional analysis
    supplier_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Supplier analysis")
    customer_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Customer analysis")
    seasonal_patterns: Optional[Dict[str, Any]] = Field(default=None, description="Seasonal patterns")


class PolicyComplianceCheck(BaseModel):
    """Individual policy compliance check."""
    
    check_name: str = Field(description="Name of the compliance check")
    required: str = Field(description="Required value/condition")
    achieved: Any = Field(description="Achieved value")
    status: str = Field(description="Check status (pass/fail/requires_additional_data)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")


class PolicyComplianceAssessment(BaseModel):
    """Overall policy compliance assessment."""
    
    bureau_score_compliance: Dict[str, PolicyComplianceCheck] = Field(
        description="Bureau score compliance checks"
    )
    coverage_compliance: Dict[str, PolicyComplianceCheck] = Field(
        description="Coverage compliance checks"
    )
    documentation_compliance: Dict[str, PolicyComplianceCheck] = Field(
        description="Documentation compliance checks"
    )
    gst_compliance_check: Dict[str, str] = Field(
        description="GST compliance check results"
    )
    
    def get_overall_status(self) -> str:
        """Get overall compliance status."""
        all_checks = []
        all_checks.extend(self.bureau_score_compliance.values())
        all_checks.extend(self.coverage_compliance.values())
        all_checks.extend(self.documentation_compliance.values())
        
        if all(check.status == "pass" for check in all_checks):
            return "pass"
        elif any(check.status == "fail" for check in all_checks):
            return "fail"
        else:
            return "requires_additional_data"


class RiskFactor(BaseModel):
    """Individual risk factor."""
    
    factor: str = Field(description="Risk factor description")
    impact: str = Field(description="Impact (positive/negative/neutral)")
    weight: float = Field(description="Weight in overall risk calculation")
    score: Optional[float] = Field(default=None, description="Individual factor score")


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment."""
    
    overall_risk_score: float = Field(description="Overall risk score (0.0 to 1.0)")
    risk_category: str = Field(description="Risk category (low/medium/high)")
    risk_grade: str = Field(description="Risk grade (A1, A2, B1, etc.)")
    
    contributing_factors: List[RiskFactor] = Field(description="Contributing risk factors")
    mitigating_factors: List[str] = Field(default_factory=list, description="Mitigating factors")
    risk_mitigation_required: bool = Field(description="Whether risk mitigation is required")
    
    # Detailed risk breakdown
    credit_risk_score: Optional[float] = Field(default=None, description="Credit risk component")
    operational_risk_score: Optional[float] = Field(default=None, description="Operational risk component")
    compliance_risk_score: Optional[float] = Field(default=None, description="Compliance risk component")
    
    def add_risk_factor(self, factor: str, impact: str, weight: float, score: Optional[float] = None) -> None:
        """Add a risk factor."""
        risk_factor = RiskFactor(factor=factor, impact=impact, weight=weight, score=score)
        self.contributing_factors.append(risk_factor)
    
    @property
    def is_low_risk(self) -> bool:
        """Check if this is low risk."""
        return self.risk_category.lower() == "low"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if this is high risk."""
        return self.risk_category.lower() == "high"


class EligibilityDetermination(BaseModel):
    """Final eligibility determination."""
    
    overall_eligibility: str = Field(description="Overall eligibility (approved/conditionally_approved/rejected)")
    approval_confidence: float = Field(description="Confidence in approval decision")
    
    conditions: List[str] = Field(default_factory=list, description="Conditions for approval")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    # Decision factors
    key_decision_factors: List[str] = Field(default_factory=list, description="Key factors in decision")
    blocking_factors: List[str] = Field(default_factory=list, description="Factors blocking approval")
    
    @property
    def is_approved(self) -> bool:
        """Check if application is approved."""
        return self.overall_eligibility in ["approved", "conditionally_approved"]
    
    @property
    def is_rejected(self) -> bool:
        """Check if application is rejected."""
        return self.overall_eligibility == "rejected"
    
    @property
    def has_conditions(self) -> bool:
        """Check if approval has conditions."""
        return len(self.conditions) > 0


class BureauVerificationResults(BaseModel):
    """Complete bureau verification results."""
    
    entity_commercial_bureau: EntityCommercialBureau = Field(description="Entity commercial bureau results")
    kmp_consumer_bureaus: List[KMPConsumerBureau] = Field(description="KMP consumer bureau results")
    partnership_cibil_compliance: Optional[PartnershipCibilCompliance] = Field(
        default=None, 
        description="Partnership CIBIL compliance (if applicable)"
    )
    
    # Summary statistics
    total_kmps_checked: int = Field(description="Total KMPs checked")
    kmps_meeting_threshold: int = Field(description="KMPs meeting CIBIL threshold")
    average_kmp_score: Optional[float] = Field(default=None, description="Average KMP CIBIL score")
    
    def get_kmp_bureau_by_id(self, kmp_id: str) -> Optional[KMPConsumerBureau]:
        """Get KMP bureau result by ID."""
        for bureau in self.kmp_consumer_bureaus:
            if bureau.kmp_id == kmp_id:
                return bureau
        return None
    
    def calculate_summary_stats(self) -> None:
        """Calculate summary statistics."""
        self.total_kmps_checked = len(self.kmp_consumer_bureaus)
        self.kmps_meeting_threshold = sum(
            1 for bureau in self.kmp_consumer_bureaus 
            if bureau.meets_cibil_threshold
        )
        
        valid_scores = [
            bureau.cibil_score for bureau in self.kmp_consumer_bureaus 
            if bureau.cibil_score is not None
        ]
        if valid_scores:
            self.average_kmp_score = sum(valid_scores) / len(valid_scores)
