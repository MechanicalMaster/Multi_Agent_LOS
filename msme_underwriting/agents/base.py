"""Base agent class for MSME loan underwriting agents."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from ..models.state import MSMELoanState
from ..models.base import ProcessingResult, ProcessingMetadata, RoutingDecision
from ..config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all MSME loan underwriting agents.
    
    This class provides common functionality for all agents including
    logging, error handling, and state management.
    """
    
    def __init__(self, agent_name: str):
        """Initialize the base agent."""
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        self.start_time: Optional[datetime] = None
        self.api_calls_made = 0
        self.total_api_cost = 0.0
    
    async def process(self, state: MSMELoanState) -> ProcessingResult:
        """
        Process the loan application state.
        
        Args:
            state: Current loan application state
            
        Returns:
            Processing result with updated data and routing decision
        """
        self.start_time = datetime.utcnow()
        self.api_calls_made = 0
        self.total_api_cost = 0.0
        
        try:
            self.logger.info(f"Starting {self.agent_name} processing for thread {state.thread_id}")
            
            # Validate prerequisites
            self._validate_prerequisites(state)
            
            # Execute agent-specific processing
            result = await self._execute_processing(state)
            
            # Create processing metadata
            end_time = datetime.utcnow()
            processing_metadata = ProcessingMetadata(
                start_time=self.start_time,
                end_time=end_time,
                total_processing_time=(end_time - self.start_time).total_seconds(),
                api_calls_made=self.api_calls_made,
                total_api_cost=self.total_api_cost
            )
            
            # Create processing result
            processing_result = ProcessingResult(
                agent_name=self.agent_name,
                processing_status="completed",
                thread_id=state.thread_id,
                processing_metadata=processing_metadata,
                next_action=result.get("next_action", "proceed"),
                routing_decision=result.get("routing_decision", self._default_routing_decision())
            )
            
            # Add agent-specific results to the processing result
            for key, value in result.items():
                if key not in ["next_action", "routing_decision"]:
                    setattr(processing_result, key, value)
            
            self.logger.info(f"Completed {self.agent_name} processing for thread {state.thread_id}")
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Error in {self.agent_name} processing: {str(e)}")
            
            # Create error processing result
            end_time = datetime.utcnow()
            processing_metadata = ProcessingMetadata(
                start_time=self.start_time or datetime.utcnow(),
                end_time=end_time,
                total_processing_time=(end_time - (self.start_time or datetime.utcnow())).total_seconds(),
                api_calls_made=self.api_calls_made,
                total_api_cost=self.total_api_cost
            )
            
            error_result = ProcessingResult(
                agent_name=self.agent_name,
                processing_status="failed",
                thread_id=state.thread_id,
                processing_metadata=processing_metadata,
                next_action="error_handling",
                routing_decision=RoutingDecision(
                    next_agent="error_handler",
                    routing_reason=f"Error in {self.agent_name}: {str(e)}",
                    conditions_met=[],
                    bypass_conditions=[]
                )
            )
            
            # Add error details
            setattr(error_result, "error", str(e))
            
            return error_result
    
    @abstractmethod
    async def _execute_processing(self, state: MSMELoanState) -> Dict[str, Any]:
        """
        Execute agent-specific processing logic.
        
        Args:
            state: Current loan application state
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    @abstractmethod
    def _validate_prerequisites(self, state: MSMELoanState) -> None:
        """
        Validate that prerequisites for this agent are met.
        
        Args:
            state: Current loan application state
            
        Raises:
            ValueError: If prerequisites are not met
        """
        pass
    
    def _default_routing_decision(self) -> RoutingDecision:
        """Get default routing decision for this agent."""
        return RoutingDecision(
            next_agent="next_agent",
            routing_reason="Default routing",
            conditions_met=[],
            bypass_conditions=[]
        )
    
    def _log_api_call(self, api_name: str, cost: float = 0.0) -> None:
        """Log an API call."""
        self.api_calls_made += 1
        self.total_api_cost += cost
        self.logger.debug(f"API call to {api_name}, cost: ${cost:.4f}")
    
    def _validate_business_rules(self, state: MSMELoanState, rule_name: str, value: Any, threshold: Any) -> bool:
        """
        Validate a business rule.
        
        Args:
            state: Current state
            rule_name: Name of the rule
            value: Value to check
            threshold: Threshold to compare against
            
        Returns:
            True if rule passes, False otherwise
        """
        try:
            if rule_name == "minimum_kmp_coverage":
                return value >= threshold
            elif rule_name == "minimum_consumer_cibil":
                return value >= threshold
            elif rule_name == "maximum_commercial_cmr":
                return value <= threshold
            elif rule_name == "eligible_constitutions":
                return value in threshold
            else:
                self.logger.warning(f"Unknown business rule: {rule_name}")
                return True
        except Exception as e:
            self.logger.error(f"Error validating business rule {rule_name}: {str(e)}")
            return False
    
    def _get_business_rule_value(self, state: MSMELoanState, rule_name: str) -> Any:
        """Get business rule value from state or settings."""
        if rule_name in state.business_rules:
            return state.business_rules[rule_name]
        
        # Fallback to settings
        return getattr(settings, rule_name, None)
    
    def _create_validation_warning(self, warning_type: str, message: str, 
                                 severity: str = "medium") -> Dict[str, Any]:
        """Create a validation warning."""
        return {
            "type": warning_type,
            "message": message,
            "severity": severity,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow()
        }
    
    def _calculate_confidence_score(self, scores: list[float]) -> float:
        """Calculate average confidence score from a list of scores."""
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    def _is_high_confidence(self, score: float) -> bool:
        """Check if a confidence score is considered high."""
        return score >= settings.high_confidence_threshold
    
    def _meets_minimum_confidence(self, score: float) -> bool:
        """Check if a confidence score meets minimum threshold."""
        return score >= settings.minimum_document_confidence
