"""Models for financial analysis."""

from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel


class TurnoverAnalysis(BaseModel):
    """Turnover analysis results."""
    
    annual_turnover_2023: Optional[float] = Field(default=None, description="Annual turnover for 2023")
    annual_turnover_2022: Optional[float] = Field(default=None, description="Annual turnover for 2022")
    annual_turnover_2021: Optional[float] = Field(default=None, description="Annual turnover for 2021")
    
    growth_rate: Optional[float] = Field(default=None, description="Year-over-year growth rate")
    cagr_3_year: Optional[float] = Field(default=None, description="3-year CAGR")
    industry_benchmark: Optional[float] = Field(default=None, description="Industry benchmark growth")
    assessment: str = Field(description="Turnover assessment (above_average/average/below_average)")
    
    # Seasonal analysis
    seasonal_patterns: Optional[Dict[str, Any]] = Field(default=None, description="Seasonal patterns")
    monthly_breakdown: Optional[List[Dict[str, Any]]] = Field(default=None, description="Monthly breakdown")
    
    @property
    def shows_growth(self) -> bool:
        """Check if turnover shows growth."""
        return self.growth_rate is not None and self.growth_rate > 0
    
    @property
    def outperforms_industry(self) -> bool:
        """Check if growth outperforms industry benchmark."""
        return (
            self.growth_rate is not None and 
            self.industry_benchmark is not None and
            self.growth_rate > self.industry_benchmark
        )


class ProfitabilityRatios(BaseModel):
    """Profitability ratio analysis."""
    
    # Margin ratios
    net_profit_margin_2023: Optional[float] = Field(default=None, description="Net profit margin 2023")
    net_profit_margin_2022: Optional[float] = Field(default=None, description="Net profit margin 2022")
    gross_profit_margin_2023: Optional[float] = Field(default=None, description="Gross profit margin 2023")
    operating_profit_margin_2023: Optional[float] = Field(default=None, description="Operating profit margin 2023")
    ebitda_margin_2023: Optional[float] = Field(default=None, description="EBITDA margin 2023")
    
    # Return ratios
    return_on_assets: Optional[float] = Field(default=None, description="Return on assets")
    return_on_equity: Optional[float] = Field(default=None, description="Return on equity")
    return_on_capital_employed: Optional[float] = Field(default=None, description="Return on capital employed")
    
    # Trend analysis
    trend: str = Field(description="Profitability trend (improving/stable/declining)")
    industry_comparison: str = Field(description="Industry comparison (favorable/average/unfavorable)")
    
    # Benchmarking
    industry_benchmarks: Optional[Dict[str, float]] = Field(default=None, description="Industry benchmarks")
    
    @property
    def is_profitable(self) -> bool:
        """Check if entity is profitable."""
        return self.net_profit_margin_2023 is not None and self.net_profit_margin_2023 > 0
    
    @property
    def margins_improving(self) -> bool:
        """Check if profit margins are improving."""
        return (
            self.net_profit_margin_2023 is not None and
            self.net_profit_margin_2022 is not None and
            self.net_profit_margin_2023 > self.net_profit_margin_2022
        )


class LiquidityRatios(BaseModel):
    """Liquidity ratio analysis."""
    
    current_ratio_2023: Optional[float] = Field(default=None, description="Current ratio 2023")
    current_ratio_2022: Optional[float] = Field(default=None, description="Current ratio 2022")
    quick_ratio_2023: Optional[float] = Field(default=None, description="Quick ratio 2023")
    cash_ratio: Optional[float] = Field(default=None, description="Cash ratio")
    
    # Working capital
    working_capital: Optional[float] = Field(default=None, description="Working capital amount")
    working_capital_ratio: Optional[float] = Field(default=None, description="Working capital ratio")
    working_capital_cycle: Optional[int] = Field(default=None, description="Working capital cycle in days")
    
    # Assessment
    assessment: str = Field(description="Liquidity assessment (excellent/adequate/poor)")
    
    # Components
    current_assets: Optional[float] = Field(default=None, description="Current assets")
    current_liabilities: Optional[float] = Field(default=None, description="Current liabilities")
    inventory: Optional[float] = Field(default=None, description="Inventory")
    receivables: Optional[float] = Field(default=None, description="Accounts receivable")
    
    @property
    def has_adequate_liquidity(self) -> bool:
        """Check if liquidity is adequate."""
        return self.current_ratio_2023 is not None and self.current_ratio_2023 >= 1.2
    
    @property
    def liquidity_improving(self) -> bool:
        """Check if liquidity is improving."""
        return (
            self.current_ratio_2023 is not None and
            self.current_ratio_2022 is not None and
            self.current_ratio_2023 > self.current_ratio_2022
        )


class LeverageRatios(BaseModel):
    """Leverage ratio analysis."""
    
    debt_equity_ratio_2023: Optional[float] = Field(default=None, description="Debt-to-equity ratio 2023")
    debt_equity_ratio_2022: Optional[float] = Field(default=None, description="Debt-to-equity ratio 2022")
    debt_service_coverage_ratio: Optional[float] = Field(default=None, description="Debt service coverage ratio")
    interest_coverage_ratio: Optional[float] = Field(default=None, description="Interest coverage ratio")
    
    # Debt components
    total_debt: Optional[float] = Field(default=None, description="Total debt")
    long_term_debt: Optional[float] = Field(default=None, description="Long-term debt")
    short_term_debt: Optional[float] = Field(default=None, description="Short-term debt")
    total_equity: Optional[float] = Field(default=None, description="Total equity")
    
    # Assessment
    assessment: str = Field(description="Leverage assessment (conservative/manageable/aggressive)")
    
    # Capacity analysis
    additional_debt_capacity: Optional[float] = Field(default=None, description="Additional debt capacity")
    optimal_debt_level: Optional[float] = Field(default=None, description="Optimal debt level")
    
    @property
    def has_manageable_leverage(self) -> bool:
        """Check if leverage is manageable."""
        return (
            self.debt_equity_ratio_2023 is not None and 
            self.debt_equity_ratio_2023 <= 2.0 and
            self.debt_service_coverage_ratio is not None and
            self.debt_service_coverage_ratio >= 1.25
        )
    
    @property
    def can_service_additional_debt(self) -> bool:
        """Check if entity can service additional debt."""
        return self.debt_service_coverage_ratio is not None and self.debt_service_coverage_ratio >= 1.5


class CashFlowAnalysis(BaseModel):
    """Cash flow analysis results."""
    
    # Operating cash flow
    operating_cash_flow: Optional[float] = Field(default=None, description="Operating cash flow")
    operating_cash_flow_margin: Optional[float] = Field(default=None, description="Operating cash flow margin")
    
    # Investing cash flow
    investing_cash_flow: Optional[float] = Field(default=None, description="Investing cash flow")
    capex: Optional[float] = Field(default=None, description="Capital expenditure")
    
    # Financing cash flow
    financing_cash_flow: Optional[float] = Field(default=None, description="Financing cash flow")
    debt_repayment: Optional[float] = Field(default=None, description="Debt repayment")
    
    # Free cash flow
    free_cash_flow: Optional[float] = Field(default=None, description="Free cash flow")
    free_cash_flow_yield: Optional[float] = Field(default=None, description="Free cash flow yield")
    
    # Stability assessment
    cash_flow_stability: str = Field(description="Cash flow stability (stable/volatile/declining)")
    cash_conversion_cycle: Optional[int] = Field(default=None, description="Cash conversion cycle in days")
    
    # Projections
    projected_cash_flows: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Projected cash flows"
    )
    
    @property
    def generates_positive_operating_cash_flow(self) -> bool:
        """Check if entity generates positive operating cash flow."""
        return self.operating_cash_flow is not None and self.operating_cash_flow > 0
    
    @property
    def has_positive_free_cash_flow(self) -> bool:
        """Check if entity has positive free cash flow."""
        return self.free_cash_flow is not None and self.free_cash_flow > 0


class LoanServicingCapacity(BaseModel):
    """Loan servicing capacity analysis."""
    
    monthly_cash_flow: Optional[float] = Field(default=None, description="Monthly cash flow")
    debt_service_capacity: Optional[float] = Field(default=None, description="Monthly debt service capacity")
    recommended_emi: Optional[float] = Field(default=None, description="Recommended EMI")
    debt_service_coverage_ratio: Optional[float] = Field(default=None, description="DSCR")
    
    # Loan sizing
    maximum_sustainable_loan: Optional[float] = Field(default=None, description="Maximum sustainable loan amount")
    
    # Requested loan analysis
    requested_loan_servicing: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Analysis of requested loan servicing"
    )
    
    # Stress testing
    stress_test_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Stress test results"
    )
    
    # Seasonal adjustments
    seasonal_adjustments: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Seasonal cash flow adjustments"
    )
    
    @property
    def can_service_requested_loan(self) -> bool:
        """Check if entity can service the requested loan."""
        if self.requested_loan_servicing is None:
            return False
        
        dscr = self.requested_loan_servicing.get("dscr_at_requested")
        return dscr is not None and dscr >= 1.25
    
    @property
    def has_adequate_dscr(self) -> bool:
        """Check if DSCR is adequate."""
        return self.debt_service_coverage_ratio is not None and self.debt_service_coverage_ratio >= 1.25


class FinancialHealthAssessment(BaseModel):
    """Complete financial health assessment."""
    
    turnover_analysis: TurnoverAnalysis = Field(description="Turnover analysis")
    profitability_ratios: ProfitabilityRatios = Field(description="Profitability ratios")
    liquidity_ratios: LiquidityRatios = Field(description="Liquidity ratios")
    leverage_ratios: LeverageRatios = Field(description="Leverage ratios")
    cash_flow_analysis: CashFlowAnalysis = Field(description="Cash flow analysis")
    
    # Overall assessment
    overall_financial_health: str = Field(description="Overall financial health (excellent/good/fair/poor)")
    financial_strength_score: Optional[float] = Field(default=None, description="Financial strength score")
    
    # Key insights
    key_strengths: List[str] = Field(default_factory=list, description="Key financial strengths")
    areas_of_concern: List[str] = Field(default_factory=list, description="Areas of concern")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    
    # Industry comparison
    industry_percentile: Optional[float] = Field(default=None, description="Industry percentile ranking")
    peer_comparison: Optional[Dict[str, Any]] = Field(default=None, description="Peer comparison")
    
    def calculate_composite_score(self) -> float:
        """Calculate composite financial health score."""
        scores = []
        
        # Profitability score (0-100)
        if self.profitability_ratios.net_profit_margin_2023 is not None:
            profit_score = min(self.profitability_ratios.net_profit_margin_2023 * 10, 100)
            scores.append(profit_score)
        
        # Liquidity score (0-100)
        if self.liquidity_ratios.current_ratio_2023 is not None:
            liquidity_score = min(self.liquidity_ratios.current_ratio_2023 * 50, 100)
            scores.append(liquidity_score)
        
        # Leverage score (0-100, inverted)
        if self.leverage_ratios.debt_equity_ratio_2023 is not None:
            leverage_score = max(100 - self.leverage_ratios.debt_equity_ratio_2023 * 25, 0)
            scores.append(leverage_score)
        
        # Cash flow score (0-100)
        if self.cash_flow_analysis.operating_cash_flow is not None:
            cf_score = 100 if self.cash_flow_analysis.operating_cash_flow > 0 else 0
            scores.append(cf_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    @property
    def is_financially_healthy(self) -> bool:
        """Check if entity is financially healthy."""
        return self.overall_financial_health in ["excellent", "good"]
    
    @property
    def meets_lending_criteria(self) -> bool:
        """Check if entity meets basic lending criteria."""
        return (
            self.profitability_ratios.is_profitable and
            self.liquidity_ratios.has_adequate_liquidity and
            self.leverage_ratios.has_manageable_leverage and
            self.cash_flow_analysis.generates_positive_operating_cash_flow
        )
