"""External API services for MSME underwriting."""

import asyncio
import httpx
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..models.base import APIResponse
from ..config import settings

logger = logging.getLogger(__name__)


class BaseAPIService:
    """Base class for external API services."""
    
    def __init__(self, service_name: str, base_url: str, api_key: Optional[str] = None):
        """Initialize base API service."""
        self.service_name = service_name
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = 30
        
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make HTTP request to external API."""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MSME-Underwriting/1.0"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response_time = response.elapsed.total_seconds()
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                    except:
                        response_data = {"raw_response": response.text}
                    
                    return APIResponse(
                        success=True,
                        data=response_data,
                        status_code=response.status_code,
                        response_time=response_time
                    )
                else:
                    error_msg = f"{self.service_name} API error: {response.status_code}"
                    logger.error(f"{error_msg} - {response.text}")
                    
                    return APIResponse(
                        success=False,
                        error=error_msg,
                        status_code=response.status_code,
                        response_time=response_time
                    )
                    
        except httpx.TimeoutException:
            error_msg = f"{self.service_name} API timeout"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg, status_code=408)
            
        except Exception as e:
            error_msg = f"{self.service_name} API error: {str(e)}"
            logger.error(error_msg)
            return APIResponse(success=False, error=error_msg, status_code=500)


class FileStorageService(BaseAPIService):
    """Service for file storage operations."""
    
    def __init__(self):
        """Initialize file storage service."""
        super().__init__("FileStorage", "http://localhost:8002")  # Example URL
    
    async def store_file(self, file_path: str, metadata: Dict[str, Any]) -> APIResponse:
        """Store a file with metadata."""
        data = {
            "file_path": file_path,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self._make_request("POST", "/store", data=data)
    
    async def retrieve_file(self, file_id: str) -> APIResponse:
        """Retrieve a file by ID."""
        return await self._make_request("GET", f"/retrieve/{file_id}")
    
    async def delete_file(self, file_id: str) -> APIResponse:
        """Delete a file by ID."""
        return await self._make_request("DELETE", f"/delete/{file_id}")


class PANValidationService(BaseAPIService):
    """Service for PAN validation."""
    
    def __init__(self):
        """Initialize PAN validation service."""
        super().__init__("PAN", "https://api.pan-validation.com", settings.pan_api_key)
    
    async def validate_pan(self, pan_number: str) -> APIResponse:
        """
        Validate PAN number and get details.
        
        Args:
            pan_number: PAN number to validate
            
        Returns:
            API response with PAN validation results
        """
        data = {
            "pan_number": pan_number,
            "consent": "Y",
            "consent_text": "I hereby declare my consent agreement for fetching my information via AADHAR & PAN APIs"
        }
        
        response = await self._make_request("POST", "/validate", data=data)
        
        if response.success and response.data:
            # Standardize response format
            pan_data = response.data
            standardized_data = {
                "pan_number": pan_number,
                "is_valid": pan_data.get("valid", False),
                "name": pan_data.get("name"),
                "category": pan_data.get("category"),
                "status": pan_data.get("status"),
                "last_updated": pan_data.get("last_updated")
            }
            response.data = standardized_data
        
        return response
    
    async def bulk_validate_pans(self, pan_numbers: List[str]) -> APIResponse:
        """Validate multiple PAN numbers."""
        data = {
            "pan_numbers": pan_numbers,
            "consent": "Y"
        }
        return await self._make_request("POST", "/bulk-validate", data=data)


class MCAService(BaseAPIService):
    """Service for MCA (Ministry of Corporate Affairs) data."""
    
    def __init__(self):
        """Initialize MCA service."""
        super().__init__("MCA", "https://api.mca.gov.in", settings.mca_api_key)
    
    async def get_company_details(self, cin: str) -> APIResponse:
        """Get company details by CIN."""
        params = {"cin": cin}
        return await self._make_request("GET", "/company-details", params=params)
    
    async def get_director_details(self, din: str) -> APIResponse:
        """Get director details by DIN."""
        params = {"din": din}
        return await self._make_request("GET", "/director-details", params=params)
    
    async def search_company_by_name(self, company_name: str) -> APIResponse:
        """Search company by name."""
        params = {"name": company_name}
        return await self._make_request("GET", "/search-company", params=params)


class CIBILService(BaseAPIService):
    """Service for CIBIL credit bureau data."""
    
    def __init__(self):
        """Initialize CIBIL service."""
        super().__init__("CIBIL", "https://api.cibil.com", settings.cibil_api_key)
    
    async def get_consumer_report(self, pan_number: str, consent: bool = True) -> APIResponse:
        """
        Get consumer credit report.
        
        Args:
            pan_number: PAN number
            consent: User consent flag
            
        Returns:
            API response with credit report
        """
        data = {
            "pan_number": pan_number,
            "consent": consent,
            "report_type": "consumer",
            "purpose": "loan_underwriting"
        }
        
        response = await self._make_request("POST", "/consumer-report", data=data)
        
        if response.success and response.data:
            # Extract key information
            report_data = response.data
            standardized_data = {
                "pan_number": pan_number,
                "cibil_score": report_data.get("score"),
                "score_date": report_data.get("score_date"),
                "credit_history_months": report_data.get("credit_history_months"),
                "total_accounts": report_data.get("total_accounts"),
                "active_accounts": report_data.get("active_accounts"),
                "overdue_accounts": report_data.get("overdue_accounts"),
                "total_exposure": report_data.get("total_exposure"),
                "overdue_amount": report_data.get("overdue_amount"),
                "enquiries_last_30_days": report_data.get("enquiries_30d"),
                "account_details": report_data.get("accounts", []),
                "enquiry_details": report_data.get("enquiries", [])
            }
            response.data = standardized_data
        
        return response
    
    async def get_commercial_report(self, pan_number: str, consent: bool = True) -> APIResponse:
        """
        Get commercial credit report.
        
        Args:
            pan_number: Entity PAN number
            consent: User consent flag
            
        Returns:
            API response with commercial credit report
        """
        data = {
            "pan_number": pan_number,
            "consent": consent,
            "report_type": "commercial",
            "purpose": "loan_underwriting"
        }
        
        response = await self._make_request("POST", "/commercial-report", data=data)
        
        if response.success and response.data:
            # Extract key information
            report_data = response.data
            standardized_data = {
                "pan_number": pan_number,
                "cmr_score": report_data.get("cmr_score"),
                "commercial_score": report_data.get("commercial_score"),
                "score_date": report_data.get("score_date"),
                "credit_history_months": report_data.get("credit_history_months"),
                "total_exposure": report_data.get("total_exposure"),
                "overdue_amount": report_data.get("overdue_amount"),
                "account_summary": report_data.get("account_summary"),
                "payment_history": report_data.get("payment_history"),
                "enquiry_summary": report_data.get("enquiry_summary")
            }
            response.data = standardized_data
        
        return response


class GSTService(BaseAPIService):
    """Service for GST data and compliance."""
    
    def __init__(self):
        """Initialize GST service."""
        super().__init__("GST", "https://api.gst.gov.in", settings.gst_api_key)
    
    async def get_gst_details(self, gst_number: str) -> APIResponse:
        """Get GST registration details."""
        params = {"gstin": gst_number}
        return await self._make_request("GET", "/taxpayer", params=params)
    
    async def get_gst_returns(self, gst_number: str, period: str) -> APIResponse:
        """
        Get GST returns for a specific period.
        
        Args:
            gst_number: GST number
            period: Period in format MMYYYY
            
        Returns:
            API response with GST returns data
        """
        params = {
            "gstin": gst_number,
            "ret_period": period
        }
        return await self._make_request("GET", "/returns", params=params)
    
    async def get_filing_status(self, gst_number: str) -> APIResponse:
        """Get GST filing status and compliance."""
        params = {"gstin": gst_number}
        response = await self._make_request("GET", "/filing-status", params=params)
        
        if response.success and response.data:
            # Calculate compliance score
            filing_data = response.data
            total_returns = filing_data.get("total_returns_due", 0)
            filed_returns = filing_data.get("returns_filed", 0)
            
            compliance_score = (filed_returns / total_returns * 100) if total_returns > 0 else 0
            
            standardized_data = {
                "gst_number": gst_number,
                "registration_status": filing_data.get("status"),
                "compliance_score": compliance_score,
                "total_returns_due": total_returns,
                "returns_filed": filed_returns,
                "pending_returns": total_returns - filed_returns,
                "last_return_filed": filing_data.get("last_return_date"),
                "filing_frequency": filing_data.get("filing_frequency")
            }
            response.data = standardized_data
        
        return response
    
    async def analyze_turnover(self, gst_number: str, start_period: str, end_period: str) -> APIResponse:
        """
        Analyze GST turnover for a period range.
        
        Args:
            gst_number: GST number
            start_period: Start period (MMYYYY)
            end_period: End period (MMYYYY)
            
        Returns:
            API response with turnover analysis
        """
        data = {
            "gstin": gst_number,
            "start_period": start_period,
            "end_period": end_period
        }
        
        response = await self._make_request("POST", "/turnover-analysis", data=data)
        
        if response.success and response.data:
            # Calculate additional metrics
            turnover_data = response.data
            monthly_turnovers = turnover_data.get("monthly_turnover", [])
            
            if monthly_turnovers:
                total_turnover = sum(monthly_turnovers)
                average_monthly = total_turnover / len(monthly_turnovers)
                
                # Calculate growth rate
                if len(monthly_turnovers) >= 2:
                    first_half = sum(monthly_turnovers[:len(monthly_turnovers)//2])
                    second_half = sum(monthly_turnovers[len(monthly_turnovers)//2:])
                    growth_rate = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
                else:
                    growth_rate = 0
                
                standardized_data = {
                    "gst_number": gst_number,
                    "analysis_period": f"{start_period} to {end_period}",
                    "total_turnover": total_turnover,
                    "average_monthly_turnover": average_monthly,
                    "turnover_growth_rate": growth_rate,
                    "monthly_breakdown": monthly_turnovers,
                    "interstate_percentage": turnover_data.get("interstate_percentage"),
                    "major_states": turnover_data.get("major_states", [])
                }
                response.data = standardized_data
        
        return response


class BureauService:
    """Unified service for credit bureau operations."""
    
    def __init__(self):
        """Initialize bureau service."""
        self.cibil_service = CIBILService()
    
    async def get_consumer_bureau_report(self, pan_number: str) -> APIResponse:
        """Get consumer bureau report (CIBIL)."""
        return await self.cibil_service.get_consumer_report(pan_number)
    
    async def get_commercial_bureau_report(self, pan_number: str) -> APIResponse:
        """Get commercial bureau report (CIBIL)."""
        return await self.cibil_service.get_commercial_report(pan_number)
    
    async def get_multiple_consumer_reports(self, pan_numbers: List[str]) -> Dict[str, APIResponse]:
        """Get consumer reports for multiple PANs."""
        tasks = [
            self.cibil_service.get_consumer_report(pan) 
            for pan in pan_numbers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            pan: result if not isinstance(result, Exception) else APIResponse(
                success=False, 
                error=str(result)
            )
            for pan, result in zip(pan_numbers, results)
        }
    
    def calculate_partnership_cibil_compliance(self, bureau_results: Dict[str, APIResponse], 
                                             threshold: int = 680) -> Dict[str, Any]:
        """
        Calculate CIBIL compliance for partnership entities.
        
        Args:
            bureau_results: Dictionary of PAN -> APIResponse
            threshold: CIBIL score threshold
            
        Returns:
            Compliance analysis
        """
        total_partners = len(bureau_results)
        partners_with_scores = 0
        partners_above_threshold = 0
        scores = []
        
        for pan, response in bureau_results.items():
            if response.success and response.data:
                cibil_score = response.data.get("cibil_score")
                if cibil_score is not None:
                    partners_with_scores += 1
                    scores.append(cibil_score)
                    if cibil_score >= threshold:
                        partners_above_threshold += 1
        
        compliance_percentage = partners_above_threshold / total_partners if total_partners > 0 else 0
        meets_50_percent_rule = compliance_percentage >= 0.5
        
        return {
            "requirement": f"50%_partners_above_{threshold}",
            "total_partners": total_partners,
            "partners_with_scores": partners_with_scores,
            "partners_above_threshold": partners_above_threshold,
            "compliance_percentage": compliance_percentage,
            "meets_50_percent_rule": meets_50_percent_rule,
            "average_score": sum(scores) / len(scores) if scores else None,
            "compliance_status": "compliant" if meets_50_percent_rule else "non_compliant",
            "additional_kmps_needed": max(0, int(total_partners * 0.5) - partners_above_threshold)
        }
