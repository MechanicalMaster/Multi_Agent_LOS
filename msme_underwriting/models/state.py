"""State models for LangGraph workflow."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal, TypedDict
from pydantic import Field
from langgraph.graph import MessagesState

from .base import BaseModel, ProcessingMetadata, RoutingDecision
from .loan_application import LoanApplication
from .documents import ClassifiedDocuments, DocumentAnalysis, MissingDocument, ValidationWarning
from .entity import EntityProfile
from .kmp import KMPAnalysis
from .verification import BureauVerificationResults, EnhancedGSTAnalysis, PolicyComplianceAssessment, RiskAssessment, EligibilityDetermination
from .financial import FinancialHealthAssessment, LoanServicingCapacity
from .banking import BankingAssessment
from .final_report import FinalReport


class AgentContext(BaseModel):
    """Context information for agent execution."""
    
    previous_agent: Optional[str] = Field(default=None, description="Name of the previous agent")
    trigger_reason: str = Field(description="Reason this agent was triggered")
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When processing started")
    retry_count: int = Field(default=0, description="Number of retries for this agent")
    timeout_seconds: int = Field(default=300, description="Timeout for this agent")


class MSMELoanState(BaseModel):
    """
    Complete state for MSME loan processing workflow.
    
    This state is shared across all agents in the LangGraph workflow and contains
    all the data needed for loan processing decisions.
    """
    
    # Core application data
    thread_id: str = Field(description="Unique thread ID for this loan application")
    loan_application: LoanApplication = Field(description="Original loan application data")
    current_step: str = Field(default="start", description="Current processing step")
    
    # Agent context
    agent_context: Optional[AgentContext] = Field(default=None, description="Current agent context")
    
    # Processing results from each agent
    agent_results: Dict[str, Any] = Field(default_factory=dict, description="Results from each agent")
    
    # Agent 1: Document Classification Results
    classified_documents: Optional[ClassifiedDocuments] = Field(
        default=None, 
        description="Classified and extracted documents"
    )
    document_analysis: Optional[DocumentAnalysis] = Field(
        default=None,
        description="Analysis of document processing"
    )
    missing_documents: List[MissingDocument] = Field(
        default_factory=list,
        description="List of missing required documents"
    )
    validation_warnings: List[ValidationWarning] = Field(
        default_factory=list,
        description="Document validation warnings"
    )
    
    # Agent 2: Entity & KMP Results
    entity_profile: Optional[EntityProfile] = Field(
        default=None,
        description="Identified entity profile"
    )
    kmp_analysis: Optional[KMPAnalysis] = Field(
        default=None,
        description="KMP identification and analysis"
    )
    basic_group_identification: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Basic group company identification"
    )
    cross_validation_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cross-validation results across documents"
    )
    
    # Agent 3: Verification & Compliance Results
    bureau_verification_results: Optional[BureauVerificationResults] = Field(
        default=None,
        description="Bureau verification results"
    )
    enhanced_gst_analysis: Optional[EnhancedGSTAnalysis] = Field(
        default=None,
        description="Enhanced GST analysis results"
    )
    pan_validation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PAN validation results"
    )
    policy_compliance_assessment: Optional[PolicyComplianceAssessment] = Field(
        default=None,
        description="Policy compliance assessment"
    )
    risk_assessment: Optional[RiskAssessment] = Field(
        default=None,
        description="Risk assessment results"
    )
    eligibility_determination: Optional[EligibilityDetermination] = Field(
        default=None,
        description="Eligibility determination"
    )
    
    # Agent 4: Financial Analysis Results
    financial_health_assessment: Optional[FinancialHealthAssessment] = Field(
        default=None,
        description="Financial health assessment"
    )
    banking_integration_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Banking integration analysis"
    )
    gst_financial_reconciliation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GST-Financial reconciliation"
    )
    loan_servicing_capacity: Optional[LoanServicingCapacity] = Field(
        default=None,
        description="Loan servicing capacity analysis"
    )
    risk_assessment_enhancement: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Enhanced risk assessment from financial analysis"
    )
    
    # Agent 7: Banking Analysis Results
    banking_assessment: Optional[BankingAssessment] = Field(
        default=None,
        description="Comprehensive banking assessment"
    )
    
    # Agent 5: Relationship Mapping Results (Phase 2)
    relationship_mapping: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Relationship mapping results"
    )
    corporate_family_tree: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Corporate family tree"
    )
    group_exposure_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Group exposure analysis"
    )
    
    # Agent 6: Final Report
    final_report: Optional[FinalReport] = Field(
        default=None,
        description="Final comprehensive report"
    )
    
    # Workflow control
    processing_metadata: Dict[str, ProcessingMetadata] = Field(
        default_factory=dict,
        description="Processing metadata for each agent"
    )
    routing_decisions: List[RoutingDecision] = Field(
        default_factory=list,
        description="History of routing decisions"
    )
    
    # Error handling
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of errors encountered during processing"
    )
    warnings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of warnings encountered during processing"
    )
    
    # Status tracking
    workflow_status: str = Field(default="in_progress", description="Overall workflow status")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Configuration
    business_rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="Business rules and thresholds"
    )
    
    def update_step(self, step: str) -> None:
        """Update the current processing step."""
        self.current_step = step
        self.last_updated = datetime.utcnow()
    
    def add_agent_result(self, agent_name: str, result: Any) -> None:
        """Add result from an agent."""
        self.agent_results[agent_name] = result
        self.last_updated = datetime.utcnow()
    
    def add_processing_metadata(self, agent_name: str, metadata: ProcessingMetadata) -> None:
        """Add processing metadata for an agent."""
        self.processing_metadata[agent_name] = metadata
        self.last_updated = datetime.utcnow()
    
    def add_routing_decision(self, decision: RoutingDecision) -> None:
        """Add a routing decision."""
        self.routing_decisions.append(decision)
        self.last_updated = datetime.utcnow()
    
    def add_error(self, agent_name: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Add an error."""
        error_entry = {
            "agent": agent_name,
            "error": error,
            "timestamp": datetime.utcnow(),
            "details": details or {}
        }
        self.errors.append(error_entry)
        self.last_updated = datetime.utcnow()
    
    def add_warning(self, agent_name: str, warning: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Add a warning."""
        warning_entry = {
            "agent": agent_name,
            "warning": warning,
            "timestamp": datetime.utcnow(),
            "details": details or {}
        }
        self.warnings.append(warning_entry)
        self.last_updated = datetime.utcnow()
    
    def get_total_processing_time(self) -> float:
        """Get total processing time across all agents."""
        return sum(
            metadata.total_processing_time 
            for metadata in self.processing_metadata.values()
        )
    
    def get_total_api_cost(self) -> float:
        """Get total API cost across all agents."""
        return sum(
            metadata.total_api_cost 
            for metadata in self.processing_metadata.values()
        )
    
    
    @property
    def current_agent_count(self) -> int:
        """Get the number of agents that have processed this application."""
        return len(self.processing_metadata)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
