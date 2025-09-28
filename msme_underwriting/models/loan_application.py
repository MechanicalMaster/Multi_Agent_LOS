"""Models for loan application data."""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from .base import BaseModel, TimestampedModel


class LoanContext(BaseModel):
    """Context information about the loan application."""
    
    loan_type: str = Field(description="Type of loan (e.g., MSM_supply_chain)")
    loan_amount: int = Field(description="Requested loan amount")
    application_timestamp: datetime = Field(description="When the application was submitted")
    purpose: Optional[str] = Field(default=None, description="Purpose of the loan")
    tenure_months: Optional[int] = Field(default=None, description="Requested tenure in months")


class UploadedFile(BaseModel):
    """Information about an uploaded file."""
    
    file_name: str = Field(description="Name of the uploaded file")
    file_path: str = Field(description="Path to the uploaded file")
    file_size: int = Field(description="Size of the file in bytes")
    upload_timestamp: datetime = Field(description="When the file was uploaded")
    file_type: str = Field(description="MIME type of the file")
    checksum: Optional[str] = Field(default=None, description="File checksum for integrity")


class ProcessingOptions(BaseModel):
    """Options for document processing."""
    
    max_pages_per_document: int = Field(default=50, description="Maximum pages to process per document")
    include_raw_responses: bool = Field(default=False, description="Include raw API responses")
    vision_model: str = Field(default="gpt-4o", description="Vision model to use for processing")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence threshold")
    enable_ocr: bool = Field(default=True, description="Enable OCR processing")
    language: str = Field(default="en", description="Document language")


class LoanApplication(TimestampedModel):
    """Complete loan application data."""
    
    thread_id: str = Field(description="Unique thread ID for this application")
    user_id: str = Field(description="ID of the user submitting the application")
    loan_context: LoanContext = Field(description="Loan context information")
    uploaded_files: List[UploadedFile] = Field(description="List of uploaded files")
    processing_options: ProcessingOptions = Field(description="Processing options")
    
    # Application status tracking
    current_step: str = Field(default="start", description="Current processing step")
    status: str = Field(default="submitted", description="Application status")
    priority: str = Field(default="normal", description="Processing priority")
    
    # Metadata
    source: str = Field(default="web", description="Application source")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    def update_step(self, step: str) -> None:
        """Update the current processing step."""
        self.current_step = step
        self.update_timestamp()
    
    def update_status(self, status: str) -> None:
        """Update the application status."""
        self.status = status
        self.update_timestamp()
    
    @property
    def total_file_size(self) -> int:
        """Calculate total size of all uploaded files."""
        return sum(file.file_size for file in self.uploaded_files)
    
    @property
    def file_count(self) -> int:
        """Get the number of uploaded files."""
        return len(self.uploaded_files)
    
    def get_files_by_type(self, file_type: str) -> List[UploadedFile]:
        """Get files filtered by MIME type."""
        return [file for file in self.uploaded_files if file.file_type == file_type]
