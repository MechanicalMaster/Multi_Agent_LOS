"""Document processing service integration."""

import asyncio
import httpx
from typing import Dict, Any, Optional
import logging

from ..models.base import APIResponse
from ..config import settings

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """
    Service for integrating with the existing PDF/Image Processing Service.
    
    This service handles communication with the external document processing
    API that extracts structured data from uploaded documents.
    """
    
    def __init__(self):
        """Initialize the document processing service."""
        self.base_url = settings.document_processing_service_url
        self.api_key = settings.document_processing_api_key
        self.timeout = 300  # 5 minutes timeout for document processing
        
    async def process_documents(self, request_payload: Dict[str, Any]) -> APIResponse:
        """
        Process documents using the external service.
        
        Args:
            request_payload: Request payload containing files and options
            
        Returns:
            API response with processed document data
        """
        try:
            logger.info(f"Processing {len(request_payload.get('files', []))} documents")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else None
            }
            
            # Remove None values from headers
            headers = {k: v for k, v in headers.items() if v is not None}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/process-documents",
                    json=request_payload,
                    headers=headers
                )
                
                response_time = response.elapsed.total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Document processing completed successfully in {response_time:.2f}s")
                    
                    return APIResponse(
                        success=True,
                        data=data,
                        status_code=response.status_code,
                        response_time=response_time
                    )
                else:
                    error_msg = f"Document processing failed with status {response.status_code}"
                    logger.error(error_msg)
                    
                    return APIResponse(
                        success=False,
                        error=error_msg,
                        status_code=response.status_code,
                        response_time=response_time
                    )
                    
        except httpx.TimeoutException:
            error_msg = "Document processing service timeout"
            logger.error(error_msg)
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=408
            )
            
        except httpx.RequestError as e:
            error_msg = f"Document processing service request error: {str(e)}"
            logger.error(error_msg)
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=500
            )
            
        except Exception as e:
            error_msg = f"Unexpected error in document processing: {str(e)}"
            logger.error(error_msg)
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=500
            )
    
    async def get_processing_status(self, job_id: str) -> APIResponse:
        """
        Get the status of a document processing job.
        
        Args:
            job_id: Job ID to check status for
            
        Returns:
            API response with job status
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}" if self.api_key else None
            }
            headers = {k: v for k, v in headers.items() if v is not None}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.base_url}/job-status/{job_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return APIResponse(
                        success=True,
                        data=data,
                        status_code=response.status_code
                    )
                else:
                    return APIResponse(
                        success=False,
                        error=f"Failed to get job status: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Error getting job status: {str(e)}",
                status_code=500
            )
    
    async def validate_document_format(self, file_path: str, file_type: str) -> bool:
        """
        Validate if a document format is supported.
        
        Args:
            file_path: Path to the file
            file_type: MIME type of the file
            
        Returns:
            True if format is supported, False otherwise
        """
        supported_types = [
            "application/pdf",
            "image/jpeg", 
            "image/jpg",
            "image/png",
            "application/zip"
        ]
        
        return file_type.lower() in supported_types
    
    async def estimate_processing_time(self, files: list) -> int:
        """
        Estimate processing time for a list of files.
        
        Args:
            files: List of files to process
            
        Returns:
            Estimated processing time in seconds
        """
        # Simple estimation based on file count and size
        base_time = 30  # Base processing time
        time_per_file = 15  # Additional time per file
        
        total_files = len(files)
        total_size = sum(file.get("file_size", 0) for file in files)
        
        # Add time based on total size (rough estimate)
        size_factor = total_size / (1024 * 1024)  # Size in MB
        size_time = size_factor * 2  # 2 seconds per MB
        
        estimated_time = base_time + (total_files * time_per_file) + size_time
        return int(estimated_time)
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported document formats."""
        return [
            "PDF documents (.pdf)",
            "JPEG images (.jpg, .jpeg)",
            "PNG images (.png)",
            "ZIP archives (.zip)"
        ]
    
    def get_processing_limits(self) -> Dict[str, Any]:
        """Get processing limits and constraints."""
        return {
            "max_file_size_mb": 50,
            "max_files_per_request": 20,
            "max_pages_per_document": 100,
            "supported_languages": ["en", "hi"],
            "timeout_seconds": self.timeout
        }
