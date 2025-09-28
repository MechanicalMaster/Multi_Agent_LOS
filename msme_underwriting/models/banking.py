"""Models for banking analysis."""

from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel


class AccountSummary(BaseModel):
    """Summary of bank accounts analyzed."""
    
    total_accounts_analyzed: int = Field(description="Total number of accounts analyzed")
    current_accounts: int = Field(default=0, description="Number of current accounts")
    savings_accounts: int = Field(default=0, description="Number of savings accounts")
    od_cc_accounts: int = Field(default=0, description="Number of OD/CC accounts")
    loan_accounts: int = Field(default=0, description="Number of loan accounts")
    
    analysis_period: str = Field(description="Period of analysis (e.g., '12 months')")
    total_statements_processed: int = Field(description="Total statements processed")
    
    # Account details
    primary_account_bank: Optional[str] = Field(default=None, description="Primary account bank")
    account_vintage: Optional[int] = Field(default=None, description="Account vintage in months")
    
    @property
    def has_multiple_accounts(self) -> bool:
        """Check if entity has multiple accounts."""
        return self.total_accounts_analyzed > 1
    
    @property
    def has_credit_facilities(self) -> bool:
        """Check if entity has credit facilities."""
        return self.od_cc_accounts > 0


class CashFlowAnalysisBank(BaseModel):
    """Cash flow analysis from banking data."""
    
    # Monthly averages
    average_monthly_credits: Optional[float] = Field(default=None, description="Average monthly credits")
    average_monthly_debits: Optional[float] = Field(default=None, description="Average monthly debits")
    net_monthly_surplus: Optional[float] = Field(default=None, description="Net monthly surplus")
    
    # Cash flow patterns
    cash_flow_consistency: str = Field(description="Cash flow consistency (high/medium/low)")
    cash_flow_volatility: Optional[float] = Field(default=None, description="Cash flow volatility coefficient")
    
    # Seasonal analysis
    seasonality_detected: Optional[str] = Field(default=None, description="Seasonality pattern")
    seasonal_adjustment_factor: Optional[float] = Field(default=None, description="Seasonal adjustment factor")
    seasonality_adjusted_flow: Optional[float] = Field(default=None, description="Seasonality adjusted cash flow")
    
    # Trend analysis
    cash_flow_trend: Optional[str] = Field(default=None, description="Cash flow trend (improving/stable/declining)")
    growth_rate: Optional[float] = Field(default=None, description="Cash flow growth rate")
    
    # Monthly breakdown
    monthly_cash_flows: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Monthly cash flow breakdown"
    )
    
    @property
    def has_positive_cash_flow(self) -> bool:
        """Check if entity has positive cash flow."""
        return self.net_monthly_surplus is not None and self.net_monthly_surplus > 0
    
    @property
    def has_consistent_cash_flow(self) -> bool:
        """Check if cash flow is consistent."""
        return self.cash_flow_consistency == "high"


class AccountConduct(BaseModel):
    """Account conduct assessment."""
    
    # Balance analysis
    average_balance: Optional[float] = Field(default=None, description="Average balance")
    minimum_balance: Optional[float] = Field(default=None, description="Minimum balance")
    maximum_balance: Optional[float] = Field(default=None, description="Maximum balance")
    balance_volatility: Optional[float] = Field(default=None, description="Balance volatility")
    
    # Credit facility utilization
    od_limit: Optional[float] = Field(default=None, description="Overdraft limit")
    cc_limit: Optional[float] = Field(default=None, description="Cash credit limit")
    od_utilization: Optional[float] = Field(default=None, description="OD utilization percentage")
    cc_utilization: Optional[float] = Field(default=None, description="CC utilization percentage")
    
    # Conduct issues
    bounce_incidents: int = Field(default=0, description="Number of bounce incidents")
    return_incidents: int = Field(default=0, description="Number of return incidents")
    penal_charges: Optional[float] = Field(default=None, description="Total penal charges")
    
    # Overall assessment
    conduct_rating: str = Field(description="Overall conduct rating (excellent/satisfactory/poor)")
    conduct_score: Optional[float] = Field(default=None, description="Numerical conduct score")
    
    # Detailed conduct history
    monthly_conduct: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Monthly conduct details"
    )
    
    @property
    def has_good_conduct(self) -> bool:
        """Check if account conduct is good."""
        return self.conduct_rating in ["excellent", "satisfactory"]
    
    @property
    def has_bounce_issues(self) -> bool:
        """Check if there are bounce issues."""
        return self.bounce_incidents > 0
    
    @property
    def utilizes_credit_facilities_well(self) -> bool:
        """Check if credit facilities are utilized well."""
        if self.od_utilization is not None:
            return 20 <= self.od_utilization <= 80
        return True


class TransactionPatterns(BaseModel):
    """Transaction pattern analysis."""
    
    # Transaction volume
    total_transactions: int = Field(description="Total number of transactions")
    average_monthly_transactions: Optional[float] = Field(default=None, description="Average monthly transactions")
    
    # Transaction types
    credit_transactions: int = Field(default=0, description="Number of credit transactions")
    debit_transactions: int = Field(default=0, description="Number of debit transactions")
    
    # Business pattern analysis
    primary_business_pattern: Optional[str] = Field(default=None, description="Primary business pattern identified")
    business_type_indicators: List[str] = Field(default_factory=list, description="Business type indicators")
    
    # Counterparty analysis
    major_counterparties: List[str] = Field(default_factory=list, description="Major counterparties")
    supplier_concentration: Optional[float] = Field(default=None, description="Supplier concentration ratio")
    customer_concentration: Optional[float] = Field(default=None, description="Customer concentration ratio")
    
    # Transaction regularity
    transaction_regularity: str = Field(description="Transaction regularity (consistent/irregular)")
    recurring_transactions: Optional[int] = Field(default=None, description="Number of recurring transactions")
    
    # Anomaly detection
    anomalies_detected: int = Field(default=0, description="Number of anomalies detected")
    anomaly_severity: str = Field(default="none", description="Anomaly severity (none/low/medium/high)")
    anomaly_details: List[Dict[str, Any]] = Field(default_factory=list, description="Anomaly details")
    
    # Digital transaction analysis
    digital_transaction_percentage: Optional[float] = Field(
        default=None,
        description="Percentage of digital transactions"
    )
    cash_transaction_percentage: Optional[float] = Field(
        default=None,
        description="Percentage of cash transactions"
    )
    
    @property
    def shows_business_activity(self) -> bool:
        """Check if transactions show genuine business activity."""
        return (
            self.total_transactions > 100 and
            self.transaction_regularity == "consistent" and
            len(self.major_counterparties) > 0
        )
    
    @property
    def has_concerning_anomalies(self) -> bool:
        """Check if there are concerning anomalies."""
        return self.anomaly_severity in ["medium", "high"]


class FinancialIntegration(BaseModel):
    """Integration analysis with financial statements."""
    
    # Reconciliation status
    reported_turnover_vs_banking: str = Field(description="Turnover reconciliation status")
    cash_flow_reconciliation: str = Field(description="Cash flow reconciliation status")
    
    # Variance analysis
    turnover_variance_percentage: Optional[float] = Field(
        default=None,
        description="Variance between reported and banking turnover"
    )
    cash_flow_variance_percentage: Optional[float] = Field(
        default=None,
        description="Variance between reported and banking cash flow"
    )
    
    # Discrepancy details
    discrepancies: str = Field(description="Level of discrepancies (minimal/moderate/significant)")
    discrepancy_explanations: List[str] = Field(
        default_factory=list,
        description="Explanations for discrepancies"
    )
    
    # Integration score
    integration_score: Optional[float] = Field(default=None, description="Integration score (0-100)")
    
    @property
    def has_good_integration(self) -> bool:
        """Check if banking data integrates well with financials."""
        return (
            self.reported_turnover_vs_banking == "consistent" and
            self.cash_flow_reconciliation == "verified" and
            self.discrepancies == "minimal"
        )


class BankingAssessment(BaseModel):
    """Complete banking assessment results."""
    
    account_summary: AccountSummary = Field(description="Account summary")
    cash_flow_analysis: CashFlowAnalysisBank = Field(description="Cash flow analysis")
    account_conduct: AccountConduct = Field(description="Account conduct assessment")
    transaction_patterns: TransactionPatterns = Field(description="Transaction patterns")
    financial_integration: FinancialIntegration = Field(description="Financial integration analysis")
    
    # Overall banking assessment
    overall_banking_score: Optional[float] = Field(default=None, description="Overall banking score")
    banking_risk_rating: Optional[str] = Field(default=None, description="Banking risk rating")
    
    # Key findings
    key_strengths: List[str] = Field(default_factory=list, description="Key banking strengths")
    areas_of_concern: List[str] = Field(default_factory=list, description="Areas of concern")
    red_flags: List[str] = Field(default_factory=list, description="Red flags identified")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Banking recommendations")
    
    # Additional analysis
    peer_comparison: Optional[Dict[str, Any]] = Field(default=None, description="Peer comparison")
    industry_benchmarks: Optional[Dict[str, Any]] = Field(default=None, description="Industry benchmarks")
    
    def calculate_overall_score(self) -> float:
        """Calculate overall banking score."""
        scores = []
        
        # Cash flow score (40% weight)
        if self.cash_flow_analysis.has_positive_cash_flow:
            cf_score = 80 if self.cash_flow_analysis.has_consistent_cash_flow else 60
        else:
            cf_score = 20
        scores.append(cf_score * 0.4)
        
        # Conduct score (30% weight)
        if self.account_conduct.conduct_score is not None:
            conduct_score = self.account_conduct.conduct_score
        else:
            conduct_score = 70 if self.account_conduct.has_good_conduct else 40
        scores.append(conduct_score * 0.3)
        
        # Transaction pattern score (20% weight)
        if self.transaction_patterns.shows_business_activity:
            pattern_score = 70 if not self.transaction_patterns.has_concerning_anomalies else 50
        else:
            pattern_score = 30
        scores.append(pattern_score * 0.2)
        
        # Integration score (10% weight)
        if self.financial_integration.integration_score is not None:
            integration_score = self.financial_integration.integration_score
        else:
            integration_score = 70 if self.financial_integration.has_good_integration else 40
        scores.append(integration_score * 0.1)
        
        return sum(scores)
    
    @property
    def supports_loan_application(self) -> bool:
        """Check if banking analysis supports loan application."""
        return (
            self.cash_flow_analysis.has_positive_cash_flow and
            self.account_conduct.has_good_conduct and
            self.transaction_patterns.shows_business_activity and
            not self.transaction_patterns.has_concerning_anomalies and
            self.financial_integration.has_good_integration
        )
    
    @property
    def has_major_red_flags(self) -> bool:
        """Check if there are major red flags."""
        return len(self.red_flags) > 0
