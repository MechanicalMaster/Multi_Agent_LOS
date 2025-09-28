"""
LangGraph orchestrator for MSME loan underwriting workflow.

This module implements the main workflow orchestrator that coordinates
the execution of all agents in the MSME loan processing pipeline.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Literal

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

# Optional PostgreSQL checkpointer - only import if available
try:
    from langgraph.checkpoint.postgres import PostgresCheckpointer
except ImportError:
    PostgresCheckpointer = None

from .models.state import MSMELoanState, AgentContext, ProcessingMetadata, RoutingDecision
from .models.loan_application import LoanApplication
from .agents import (
    DocumentClassificationAgent,
    EntityKMPIdentificationAgent,
    VerificationComplianceAgent,
    FinancialAnalysisAgent,
    BankingAnalysisAgent,
    FinalAssemblyAgent,
)
from .config import settings

logger = logging.getLogger(__name__)


class MSMELoanOrchestrator:
    """
    Main orchestrator for MSME loan processing workflow.
    
    This class manages the execution flow of all agents and handles
    state transitions, error handling, and routing decisions.
    """
    
    def __init__(self, checkpointer: Optional[Any] = None):
        """Initialize the orchestrator."""
        self.checkpointer = checkpointer
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents."""
        return {
            "document_classification": DocumentClassificationAgent(),
            "entity_kmp_identification": EntityKMPIdentificationAgent(),
            "verification_compliance": VerificationComplianceAgent(),
            "financial_analysis": FinancialAnalysisAgent(),
            "banking_analysis": BankingAnalysisAgent(),
            "final_assembly": FinalAssemblyAgent(),
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the state graph
        builder = StateGraph(MSMELoanState)
        
        # Add agent nodes
        builder.add_node("document_classification", self._document_classification_node)
        builder.add_node("entity_kmp_identification", self._entity_kmp_identification_node)
        builder.add_node("verification_compliance", self._verification_compliance_node)
        builder.add_node("financial_analysis", self._financial_analysis_node)
        builder.add_node("banking_analysis", self._banking_analysis_node)
        builder.add_node("final_assembly", self._final_assembly_node)
        
        # Add error handling node
        builder.add_node("error_handler", self._error_handler_node)
        
        # Add human review node
        builder.add_node("human_review", self._human_review_node)
        
        # Define the workflow edges
        builder.add_edge(START, "document_classification")
        
        # Conditional edges based on routing decisions
        builder.add_conditional_edges(
            "document_classification",
            self._route_from_document_classification,
            {
                "entity_kmp_identification": "entity_kmp_identification",
                "human_review": "human_review",
                "error_handler": "error_handler",
            }
        )
        
        builder.add_conditional_edges(
            "entity_kmp_identification",
            self._route_from_entity_kmp,
            {
                "verification_compliance": "verification_compliance",
                "human_review": "human_review",
                "error_handler": "error_handler",
            }
        )
        
        builder.add_conditional_edges(
            "verification_compliance",
            self._route_from_verification,
            {
                "financial_analysis": "financial_analysis",
                "human_review": "human_review",
                "error_handler": "error_handler",
            }
        )
        
        builder.add_conditional_edges(
            "financial_analysis",
            self._route_from_financial,
            {
                "banking_analysis": "banking_analysis",
                "human_review": "human_review",
                "error_handler": "error_handler",
            }
        )
        
        builder.add_conditional_edges(
            "banking_analysis",
            self._route_from_banking,
            {
                "final_assembly": "final_assembly",
                "human_review": "human_review",
                "error_handler": "error_handler",
            }
        )
        
        builder.add_edge("final_assembly", END)
        builder.add_edge("human_review", END)
        builder.add_edge("error_handler", END)
        
        # Compile the graph
        return builder.compile(checkpointer=self.checkpointer)
    
    async def _document_classification_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document classification agent."""
        try:
            # Convert dict to MSMELoanState if needed
            if isinstance(state, dict):
                # Create MSMELoanState from dict
                loan_state = MSMELoanState(**state)
            else:
                loan_state = state
                
            logger.info(f"Starting document classification for thread {loan_state.thread_id}")
            
            # Set agent context
            loan_state.agent_context = AgentContext(
                trigger_reason="workflow_start",
                processing_timestamp=datetime.utcnow()
            )
            loan_state.update_step("document_classification")
            
            # Execute agent
            agent = self.agents["document_classification"]
            result = await agent.process(loan_state)
            
            # Update state with results
            loan_state.classified_documents = result.classified_documents
            loan_state.document_analysis = result.document_analysis
            loan_state.missing_documents = result.missing_documents
            loan_state.validation_warnings = result.validation_warnings
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=loan_state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - loan_state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            loan_state.add_processing_metadata("document_classification", metadata)
            
            # Determine routing
            routing_decision = self._determine_document_classification_routing(result)
            loan_state.add_routing_decision(routing_decision)
            
            # Return updated state as dict
            return loan_state.model_dump()
            
        except Exception as e:
            logger.error(f"Error in document classification: {str(e)}")
            # Convert dict to MSMELoanState if needed for error handling
            if isinstance(state, dict):
                loan_state = MSMELoanState(**state)
            else:
                loan_state = state
            loan_state.add_error("document_classification", str(e))
            loan_state.workflow_status = "error"
            return loan_state.model_dump()
    
    async def _entity_kmp_identification_node(self, state: MSMELoanState) -> Command[Literal["verification_compliance", "human_review", "error_handler"]]:
        """Execute entity and KMP identification agent."""
        try:
            logger.info(f"Starting entity KMP identification for thread {state.thread_id}")
            
            # Set agent context
            state.agent_context = AgentContext(
                previous_agent="document_classification",
                trigger_reason="documents_classified_successfully",
                processing_timestamp=datetime.utcnow()
            )
            state.update_step("entity_kmp_identification")
            
            # Execute agent
            agent = self.agents["entity_kmp_identification"]
            result = await agent.process(state)
            
            # Update state with results
            state.entity_profile = result.entity_profile
            state.kmp_analysis = result.kmp_analysis
            state.basic_group_identification = result.basic_group_identification
            state.cross_validation_results = result.cross_validation_results
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            state.add_processing_metadata("entity_kmp_identification", metadata)
            
            # Determine routing
            routing_decision = self._determine_entity_kmp_routing(result)
            state.add_routing_decision(routing_decision)
            
            return Command(goto=routing_decision.next_agent)
            
        except Exception as e:
            logger.error(f"Error in entity KMP identification: {str(e)}")
            state.add_error("entity_kmp_identification", str(e))
            return Command(goto="error_handler")
    
    async def _verification_compliance_node(self, state: MSMELoanState) -> Command[Literal["financial_analysis", "human_review", "error_handler"]]:
        """Execute verification and compliance agent."""
        try:
            logger.info(f"Starting verification compliance for thread {state.thread_id}")
            
            # Set agent context
            state.agent_context = AgentContext(
                previous_agent="entity_kmp_identification",
                trigger_reason="minimum_coverage_achieved",
                processing_timestamp=datetime.utcnow()
            )
            state.update_step("verification_compliance")
            
            # Execute agent
            agent = self.agents["verification_compliance"]
            result = await agent.process(state)
            
            # Update state with results
            state.bureau_verification_results = result.bureau_verification_results
            state.enhanced_gst_analysis = result.enhanced_gst_analysis
            state.pan_validation = result.pan_validation
            state.policy_compliance_assessment = result.policy_compliance_assessment
            state.risk_assessment = result.risk_assessment
            state.eligibility_determination = result.eligibility_determination
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            state.add_processing_metadata("verification_compliance", metadata)
            
            # Determine routing
            routing_decision = self._determine_verification_routing(result)
            state.add_routing_decision(routing_decision)
            
            return Command(goto=routing_decision.next_agent)
            
        except Exception as e:
            logger.error(f"Error in verification compliance: {str(e)}")
            state.add_error("verification_compliance", str(e))
            return Command(goto="error_handler")
    
    async def _financial_analysis_node(self, state: MSMELoanState) -> Command[Literal["banking_analysis", "human_review", "error_handler"]]:
        """Execute financial analysis agent."""
        try:
            logger.info(f"Starting financial analysis for thread {state.thread_id}")
            
            # Set agent context
            state.agent_context = AgentContext(
                previous_agent="verification_compliance",
                trigger_reason="comprehensive_analysis_required",
                processing_timestamp=datetime.utcnow()
            )
            state.update_step("financial_analysis")
            
            # Execute agent
            agent = self.agents["financial_analysis"]
            result = await agent.process(state)
            
            # Update state with results
            state.financial_health_assessment = result.financial_health_assessment
            state.banking_integration_analysis = result.banking_integration_analysis
            state.gst_financial_reconciliation = result.gst_financial_reconciliation
            state.loan_servicing_capacity = result.loan_servicing_capacity
            state.risk_assessment_enhancement = result.risk_assessment_enhancement
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            state.add_processing_metadata("financial_analysis", metadata)
            
            # Determine routing
            routing_decision = self._determine_financial_routing(result)
            state.add_routing_decision(routing_decision)
            
            return Command(goto=routing_decision.next_agent)
            
        except Exception as e:
            logger.error(f"Error in financial analysis: {str(e)}")
            state.add_error("financial_analysis", str(e))
            return Command(goto="error_handler")
    
    async def _banking_analysis_node(self, state: MSMELoanState) -> Command[Literal["final_assembly", "human_review", "error_handler"]]:
        """Execute banking analysis agent."""
        try:
            logger.info(f"Starting banking analysis for thread {state.thread_id}")
            
            # Set agent context
            state.agent_context = AgentContext(
                previous_agent="financial_analysis",
                trigger_reason="banking_validation_required",
                processing_timestamp=datetime.utcnow()
            )
            state.update_step("banking_analysis")
            
            # Execute agent
            agent = self.agents["banking_analysis"]
            result = await agent.process(state)
            
            # Update state with results
            state.banking_assessment = result.banking_assessment
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            state.add_processing_metadata("banking_analysis", metadata)
            
            # Determine routing
            routing_decision = self._determine_banking_routing(result)
            state.add_routing_decision(routing_decision)
            
            return Command(goto=routing_decision.next_agent)
            
        except Exception as e:
            logger.error(f"Error in banking analysis: {str(e)}")
            state.add_error("banking_analysis", str(e))
            return Command(goto="error_handler")
    
    async def _final_assembly_node(self, state: MSMELoanState) -> MSMELoanState:
        """Execute final assembly agent."""
        try:
            logger.info(f"Starting final assembly for thread {state.thread_id}")
            
            # Set agent context
            state.agent_context = AgentContext(
                previous_agent="banking_analysis",
                trigger_reason="all_analysis_completed",
                processing_timestamp=datetime.utcnow()
            )
            state.update_step("final_assembly")
            
            # Execute agent
            agent = self.agents["final_assembly"]
            result = await agent.process(state)
            
            # Update state with results
            state.final_report = result.final_report
            state.workflow_status = "completed"
            
            # Add processing metadata
            metadata = ProcessingMetadata(
                start_time=state.agent_context.processing_timestamp,
                end_time=datetime.utcnow(),
                total_processing_time=(datetime.utcnow() - state.agent_context.processing_timestamp).total_seconds(),
                api_calls_made=result.processing_metadata.api_calls_made,
                total_api_cost=result.processing_metadata.total_api_cost
            )
            state.add_processing_metadata("final_assembly", metadata)
            
            logger.info(f"Completed loan processing for thread {state.thread_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error in final assembly: {str(e)}")
            state.add_error("final_assembly", str(e))
            state.workflow_status = "error"
            return state
    
    async def _error_handler_node(self, state: MSMELoanState) -> MSMELoanState:
        """Handle errors in the workflow."""
        logger.error(f"Error handler triggered for thread {state.thread_id}")
        state.workflow_status = "error"
        state.update_step("error_handling")
        return state
    
    async def _human_review_node(self, state: MSMELoanState) -> MSMELoanState:
        """Handle human review requirements."""
        logger.info(f"Human review required for thread {state.thread_id}")
        state.workflow_status = "human_review_required"
        state.update_step("human_review")
        return state
    
    # Routing decision methods
    def _route_from_document_classification(self, state: MSMELoanState) -> str:
        """Route from document classification based on results."""
        if state.has_errors:
            return "error_handler"
        
        # Check if we have sufficient documents
        if (state.classified_documents and 
            len(state.classified_documents.borrower_documents.get("pan_cards", [])) > 0):
            return "entity_kmp_identification"
        else:
            return "human_review"
    
    def _route_from_entity_kmp(self, state: MSMELoanState) -> str:
        """Route from entity KMP identification based on results."""
        if state.has_errors:
            return "error_handler"
        
        # Check if minimum KMP coverage is met
        if (state.kmp_analysis and 
            state.kmp_analysis.kmp_coverage_analysis.coverage_percentage >= 0.5):
            return "verification_compliance"
        else:
            return "human_review"
    
    def _route_from_verification(self, state: MSMELoanState) -> str:
        """Route from verification based on results."""
        if state.has_errors:
            return "error_handler"
        
        # Check eligibility determination
        if (state.eligibility_determination and 
            state.eligibility_determination.overall_eligibility != "rejected"):
            return "financial_analysis"
        else:
            return "human_review"
    
    def _route_from_financial(self, state: MSMELoanState) -> str:
        """Route from financial analysis based on results."""
        if state.has_errors:
            return "error_handler"
        
        # Check if we have banking documents for analysis
        if (state.classified_documents and 
            len(state.classified_documents.banking_documents) > 0):
            return "banking_analysis"
        else:
            return "human_review"
    
    def _route_from_banking(self, state: MSMELoanState) -> str:
        """Route from banking analysis based on results."""
        if state.has_errors:
            return "error_handler"
        
        # Always proceed to final assembly after banking analysis
        return "final_assembly"
    
    # Helper methods for routing decisions
    def _determine_document_classification_routing(self, result: Any) -> RoutingDecision:
        """Determine routing decision from document classification."""
        if result.routing_decision.next_agent == "entity_kmp_identification":
            return RoutingDecision(
                next_agent="entity_kmp_identification",
                routing_reason="Sufficient documents available for entity analysis",
                conditions_met=["borrower_pan_available", "documents_classified"]
            )
        else:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Insufficient documents for automated processing",
                conditions_met=[]
            )
    
    def _determine_entity_kmp_routing(self, result: Any) -> RoutingDecision:
        """Determine routing decision from entity KMP identification."""
        if result.routing_decision.next_agent == "verification_compliance":
            return RoutingDecision(
                next_agent="verification_compliance",
                routing_reason="Minimum KMP coverage achieved",
                conditions_met=["entity_identified", "minimum_coverage_achieved"]
            )
        else:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Insufficient KMP coverage",
                conditions_met=[]
            )
    
    def _determine_verification_routing(self, result: Any) -> RoutingDecision:
        """Determine routing decision from verification."""
        if result.routing_decision.next_agent == "financial_analysis":
            return RoutingDecision(
                next_agent="financial_analysis",
                routing_reason="Basic compliance checks passed",
                conditions_met=["bureau_scores_passed", "compliance_verified"]
            )
        else:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Compliance issues require manual review",
                conditions_met=[]
            )
    
    def _determine_financial_routing(self, result: Any) -> RoutingDecision:
        """Determine routing decision from financial analysis."""
        if result.routing_decision.next_agent == "banking_analysis":
            return RoutingDecision(
                next_agent="banking_analysis",
                routing_reason="Financial analysis complete, banking validation required",
                conditions_met=["financial_statements_analyzed", "servicing_capacity_calculated"]
            )
        else:
            return RoutingDecision(
                next_agent="human_review",
                routing_reason="Financial analysis requires manual review",
                conditions_met=[]
            )
    
    def _determine_banking_routing(self, result: Any) -> RoutingDecision:
        """Determine routing decision from banking analysis."""
        return RoutingDecision(
            next_agent="final_assembly",
            routing_reason="Banking analysis complete, ready for final assembly",
            conditions_met=["banking_analysis_completed"]
        )
    
    async def process_loan_application(self, loan_application: LoanApplication) -> MSMELoanState:
        """
        Process a loan application through the complete workflow.
        
        Args:
            loan_application: The loan application to process
            
        Returns:
            Final state after processing
        """
        # Initialize state
        initial_state = MSMELoanState(
            thread_id=loan_application.thread_id,
            loan_application=loan_application,
            messages=[],  # Required by MessagesState
            business_rules={
                "minimum_kmp_coverage": settings.minimum_kmp_coverage,
                "minimum_consumer_cibil": settings.minimum_consumer_cibil,
                "maximum_commercial_cmr": settings.maximum_commercial_cmr,
                "eligible_constitutions": settings.eligible_constitutions,
            }
        )
        
        # Configure the run
        config = RunnableConfig(
            configurable={
                "thread_id": loan_application.thread_id,
                "checkpoint_ns": "msme_loan_processing"
            }
        )
        
        # Execute the workflow
        try:
            final_state = await self.graph.ainvoke(initial_state, config=config)
            return final_state
        except Exception as e:
            logger.error(f"Error processing loan application {loan_application.thread_id}: {str(e)}")
            initial_state.add_error("orchestrator", str(e))
            initial_state.workflow_status = "error"
            return initial_state
    
    async def get_state(self, thread_id: str) -> Optional[MSMELoanState]:
        """Get the current state for a thread."""
        if not self.checkpointer:
            return None
        
        config = RunnableConfig(
            configurable={
                "thread_id": thread_id,
                "checkpoint_ns": "msme_loan_processing"
            }
        )
        
        try:
            state = await self.graph.aget_state(config)
            return state.values if state else None
        except Exception as e:
            logger.error(f"Error getting state for thread {thread_id}: {str(e)}")
            return None
    
    async def resume_processing(self, thread_id: str, user_input: Optional[Dict[str, Any]] = None) -> MSMELoanState:
        """Resume processing from a checkpoint."""
        config = RunnableConfig(
            configurable={
                "thread_id": thread_id,
                "checkpoint_ns": "msme_loan_processing"
            }
        )
        
        try:
            # If user input is provided, update the state
            if user_input:
                await self.graph.aupdate_state(config, user_input)
            
            # Resume processing
            final_state = await self.graph.ainvoke(None, config=config)
            return final_state
        except Exception as e:
            logger.error(f"Error resuming processing for thread {thread_id}: {str(e)}")
            # Return error state
            error_state = MSMELoanState(
                thread_id=thread_id,
                messages=[],
                workflow_status="error"
            )
            error_state.add_error("orchestrator", str(e))
            return error_state
