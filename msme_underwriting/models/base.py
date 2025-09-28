"""Base models for the MSME underwriting system."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""
    
    model_config = ConfigDict(
        # Allow extra fields for flexibility
        extra="allow",
        # Use enum values instead of names
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
        # Allow population by field name
        populate_by_name=True,
        # Serialize by alias
        ser_by_alias=True,
    )


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class ProcessingResult(BaseModel):
    """Base class for agent processing results."""
    
    agent_name: str = Field(description="Name of the agent that processed this")
    processing_status: str = Field(description="Processing status (completed, failed, partial)")
    thread_id: str = Field(description="Thread ID for this processing session")
    processing_metadata: "ProcessingMetadata" = Field(description="Processing metadata")
    next_action: str = Field(description="Next action to take")
    routing_decision: "RoutingDecision" = Field(description="Routing decision for next agent")


class ProcessingMetadata(BaseModel):
    """Metadata about processing operations."""
    
    start_time: datetime = Field(description="Processing start time")
    end_time: datetime = Field(description="Processing end time")
    total_processing_time: float = Field(description="Total processing time in seconds")
    api_calls_made: int = Field(default=0, description="Number of API calls made")
    total_api_cost: float = Field(default=0.0, description="Total API cost")
    
    @property
    def processing_duration(self) -> float:
        """Calculate processing duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()


class RoutingDecision(BaseModel):
    """Decision about routing to next agent."""
    
    next_agent: str = Field(description="Name of the next agent to route to")
    routing_reason: str = Field(description="Reason for this routing decision")
    conditions_met: list[str] = Field(default_factory=list, description="Conditions that were met")
    bypass_conditions: list[str] = Field(default_factory=list, description="Conditions that were bypassed")


class ValidationResult(BaseModel):
    """Result of a validation check."""
    
    check_name: str = Field(description="Name of the validation check")
    status: str = Field(description="Status (passed, failed, warning)")
    value: Optional[Any] = Field(default=None, description="Value that was checked")
    expected: Optional[Any] = Field(default=None, description="Expected value")
    message: Optional[str] = Field(default=None, description="Validation message")
    severity: str = Field(default="info", description="Severity level")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool = Field(description="Whether the API call was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    response_time: Optional[float] = Field(default=None, description="Response time in seconds")


# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass
