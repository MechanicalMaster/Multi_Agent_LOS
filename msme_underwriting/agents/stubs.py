"""
Stub implementations for agents not yet fully implemented.

These stubs allow the system to run without crashing while the full
agent implementations are being developed.
"""

from typing import Dict, Any
from datetime import datetime

from ..models.state import MSMELoanState
from ..models.base import RoutingDecision
from .base import BaseAgent


class EntityKMPIdentificationAgent(BaseAgent):
    """Stub for Agent 2: Entity & KMP Identification Agent."""
    
    def __init__(self):
        super().__init__("entity_kmp_identification")
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for entity KMP identification."""
        if not state.classified_documents:
            raise ValueError("Classified documents are required")
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Stub implementation - returns placeholder data."""
        self.logger.info("🚧 STUB: Entity KMP Identification Agent - Not yet implemented")
        
        # Return minimal data to allow workflow to continue
        return {
            "entity_profile": None,
            "kmp_analysis": None,
            "basic_group_identification": None,
            "cross_validation_results": {},
            "next_action": "proceed_to_verification",
            "routing_decision": RoutingDecision(
                next_agent="human_review",
                routing_reason="Agent not yet implemented - routing to human review",
                conditions_met=[],
                bypass_conditions=["agent_not_implemented"]
            )
        }


class VerificationComplianceAgent(BaseAgent):
    """Stub for Agent 3: Verification & Compliance Agent."""
    
    def __init__(self):
        super().__init__("verification_compliance")
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for verification compliance."""
        if not state.entity_profile and not state.kmp_analysis:
            raise ValueError("Entity profile or KMP analysis is required")
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Stub implementation - returns placeholder data."""
        self.logger.info("🚧 STUB: Verification Compliance Agent - Not yet implemented")
        
        return {
            "bureau_verification_results": None,
            "enhanced_gst_analysis": None,
            "pan_validation": None,
            "policy_compliance_assessment": None,
            "risk_assessment": None,
            "eligibility_determination": None,
            "next_action": "proceed_to_financial_analysis",
            "routing_decision": RoutingDecision(
                next_agent="human_review",
                routing_reason="Agent not yet implemented - routing to human review",
                conditions_met=[],
                bypass_conditions=["agent_not_implemented"]
            )
        }


class FinancialAnalysisAgent(BaseAgent):
    """Stub for Agent 4: Financial Analysis Agent."""
    
    def __init__(self):
        super().__init__("financial_analysis")
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for financial analysis."""
        if not state.classified_documents:
            raise ValueError("Classified documents are required")
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Stub implementation - returns placeholder data."""
        self.logger.info("🚧 STUB: Financial Analysis Agent - Not yet implemented")
        
        return {
            "financial_health_assessment": None,
            "banking_integration_analysis": None,
            "gst_financial_reconciliation": None,
            "loan_servicing_capacity": None,
            "risk_assessment_enhancement": None,
            "next_action": "proceed_to_banking_analysis",
            "routing_decision": RoutingDecision(
                next_agent="human_review",
                routing_reason="Agent not yet implemented - routing to human review",
                conditions_met=[],
                bypass_conditions=["agent_not_implemented"]
            )
        }


class BankingAnalysisAgent(BaseAgent):
    """Stub for Agent 7: Banking Analysis Agent."""
    
    def __init__(self):
        super().__init__("banking_analysis")
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for banking analysis."""
        if not state.classified_documents:
            raise ValueError("Classified documents are required")
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Stub implementation - returns placeholder data."""
        self.logger.info("🚧 STUB: Banking Analysis Agent - Not yet implemented")
        
        return {
            "banking_assessment": None,
            "next_action": "proceed_to_final_assembly",
            "routing_decision": RoutingDecision(
                next_agent="human_review",
                routing_reason="Agent not yet implemented - routing to human review",
                conditions_met=[],
                bypass_conditions=["agent_not_implemented"]
            )
        }


class FinalAssemblyAgent(BaseAgent):
    """Stub for Agent 6: Final Assembly & Report Generation Agent."""
    
    def __init__(self):
        super().__init__("final_assembly")
    
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """Validate prerequisites for final assembly."""
        # Final assembly can work with whatever data is available
        pass
    
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """Stub implementation - returns placeholder data."""
        self.logger.info("🚧 STUB: Final Assembly Agent - Not yet implemented")
        
        # Import here to avoid circular imports
        from ..models.final_report import (
            FinalReport, ExecutiveSummary, ComprehensiveBorrowerProfile,
            EntitySummary, FinancialSummary, BankingSummary,
            VerificationSummary, RiskAssessmentSummary, LoanRecommendation,
            ProcessingSummary, QualityMetrics, ScoreSummary, CibilSummary,
            ComplianceStatus, ProposedTerms
        )
        
        # Create a minimal final report for testing
        final_report = FinalReport(
            report_id=f"STUB_REPORT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            thread_id=state.thread_id,
            executive_summary=ExecutiveSummary(
                application_id=state.thread_id,
                borrower_name="STUB - Not Yet Processed",
                loan_request={
                    "amount": state.loan_application.loan_context.loan_amount,
                    "type": state.loan_application.loan_context.loan_type,
                    "purpose": "Working capital financing"
                },
                recommendation="REQUIRES MANUAL REVIEW",
                risk_grade="PENDING",
                processing_confidence=0.0,
                recommended_loan_amount=0
            ),
            comprehensive_borrower_profile=ComprehensiveBorrowerProfile(
                entity_summary=EntitySummary(
                    legal_name="STUB - Entity Not Processed",
                    constitution="Unknown",
                    pan_number="STUB000000",
                    registered_address="Not processed yet"
                ),
                kmp_summary=[],
                financial_summary=FinancialSummary(
                    annual_turnover="Not processed",
                    growth_rate="Not processed",
                    net_profit_margin="Not processed",
                    debt_equity_ratio="Not processed",
                    working_capital="Not processed",
                    debt_service_capacity="Not processed"
                ),
                banking_summary=BankingSummary(
                    accounts_analyzed=0,
                    average_balance="Not processed",
                    monthly_cash_flow="Not processed",
                    account_conduct="Not processed"
                )
            ),
            verification_summary=VerificationSummary(
                entity_commercial_score=ScoreSummary(
                    status="Not processed"
                ),
                kmp_consumer_scores=CibilSummary(
                    all_above_threshold=False
                ),
                compliance_status=ComplianceStatus(
                    gst_compliance="Not processed",
                    pan_validation="Not processed",
                    documentation="Not processed"
                )
            ),
            risk_assessment_summary=RiskAssessmentSummary(
                overall_risk_score=1.0,
                risk_category="Unknown",
                risk_grade="PENDING",
                key_strengths=[],
                areas_of_concern=["Agents not yet implemented"],
                recommended_mitigations=["Complete agent implementation"]
            ),
            loan_recommendation=LoanRecommendation(
                primary_recommendation="MANUAL REVIEW REQUIRED",
                confidence_level="Low (0%)",
                recommended_loan_amount=0,
                suggested_conditions=["Complete system implementation"],
                proposed_terms=ProposedTerms(
                    loan_amount=0,
                    tenure="TBD",
                    interest_rate="TBD",
                    emi="TBD",
                    dscr=0.0
                ),
                estimated_processing_timeline="Pending implementation",
                next_steps=["Implement remaining agents", "Process application manually"]
            ),
            processing_summary=ProcessingSummary(
                total_processing_time=0.0,
                agents_executed=["document_classification"],
                total_api_calls=0,
                total_api_cost=0.0
            ),
            quality_metrics=QualityMetrics(
                document_confidence_average=0.0,
                data_completeness_score=0.0,
                cross_validation_score=0.0,
                manual_review_required=True
            )
        )
        
        return {
            "final_report": final_report,
            "next_action": "workflow_complete",
            "routing_decision": RoutingDecision(
                next_agent="END",
                routing_reason="Stub final assembly completed",
                conditions_met=["stub_processing_complete"],
                bypass_conditions=[]
            )
        }
