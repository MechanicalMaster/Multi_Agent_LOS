"""Models for entity identification and profiling."""

from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel, ValidationResult


class ConstitutionEligibility(BaseModel):
    """Entity constitution eligibility assessment."""
    
    eligible_types: List[str] = Field(description="List of eligible constitution types")
    detected_type: str = Field(description="Detected constitution type")
    is_eligible: bool = Field(description="Whether the detected type is eligible")
    validation_checks: List[ValidationResult] = Field(description="Validation checks performed")
    confidence: float = Field(description="Confidence in constitution determination")


class DateOfEstablishment(BaseModel):
    """Date of establishment determination."""
    
    determined_date: str = Field(description="Determined establishment date")
    source_document: str = Field(description="Source document for the date")
    hierarchy_used: List[str] = Field(description="Document hierarchy used for determination")
    confidence: float = Field(description="Confidence in date determination")
    alternative_dates: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative dates found in other documents"
    )


class RegisteredAddress(BaseModel):
    """Standardized registered address."""
    
    line1: str = Field(description="Address line 1")
    line2: Optional[str] = Field(default=None, description="Address line 2")
    city: str = Field(description="City")
    state: str = Field(description="State")
    pincode: str = Field(description="PIN code")
    country: str = Field(default="India", description="Country")
    standardized: bool = Field(description="Whether address has been standardized")
    
    # Validation results
    validation_status: Optional[str] = Field(default=None, description="Address validation status")
    validation_score: Optional[float] = Field(default=None, description="Address validation score")
    
    def get_full_address(self) -> str:
        """Get full formatted address."""
        parts = [self.line1]
        if self.line2:
            parts.append(self.line2)
        parts.extend([self.city, self.state, self.pincode, self.country])
        return ", ".join(parts)


class BorrowingEntity(BaseModel):
    """Information about the borrowing entity."""
    
    pan_number: str = Field(description="Entity PAN number")
    entity_name: str = Field(description="Legal entity name")
    constitution: str = Field(description="Entity constitution type")
    constitution_source: str = Field(description="Source of constitution determination")
    constitution_eligibility: ConstitutionEligibility = Field(description="Constitution eligibility assessment")
    
    # API verification
    api_verified: bool = Field(description="Whether entity is API verified")
    verified_name: Optional[str] = Field(default=None, description="API verified name")
    
    # Registration details
    gst_number: Optional[str] = Field(default=None, description="GST number")
    udyam_number: Optional[str] = Field(default=None, description="Udyam registration number")
    cin_number: Optional[str] = Field(default=None, description="CIN number (for companies)")
    llpin_number: Optional[str] = Field(default=None, description="LLPIN number (for LLPs)")
    
    # Establishment details
    date_of_establishment: DateOfEstablishment = Field(description="Date of establishment")
    registered_address: RegisteredAddress = Field(description="Registered address")
    
    # Business details
    business_activity: Optional[str] = Field(default=None, description="Primary business activity")
    industry_code: Optional[str] = Field(default=None, description="Industry classification code")
    msme_classification: Optional[str] = Field(default=None, description="MSME classification")
    
    # Validation
    entity_validation_score: float = Field(description="Overall entity validation score")
    validation_flags: List[str] = Field(default_factory=list, description="Validation flags")
    
    def get_constitution_from_pan(self) -> str:
        """Determine constitution from PAN 4th character."""
        if len(self.pan_number) >= 4:
            fourth_char = self.pan_number[3].upper()
            constitution_map = {
                'A': 'association_of_persons',
                'B': 'body_of_individuals', 
                'C': 'company',
                'D': 'partnership',
                'E': 'trust',
                'F': 'firm',
                'G': 'government',
                'H': 'huf',
                'J': 'artificial_juridical_person',
                'K': 'krishi_upaj_mandi_samiti',
                'L': 'local_authority',
                'N': 'non_resident',
                'P': 'individual',
                'T': 'trust_ait',
            }
            return constitution_map.get(fourth_char, 'unknown')
        return 'unknown'
    
    @property
    def is_msme_eligible(self) -> bool:
        """Check if entity is eligible for MSME loans."""
        eligible_constitutions = [
            'sole_proprietorship', 'partnership', 'llp', 'company', 'huf'
        ]
        return self.constitution in eligible_constitutions


class EntityProfile(BaseModel):
    """Complete entity profile."""
    
    borrowing_entity: BorrowingEntity = Field(description="Primary borrowing entity details")
    
    # Related entities (for future group analysis)
    related_entities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Related entities identified"
    )
    
    # Validation summary
    validation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of all validation checks"
    )
    
    # Risk indicators
    risk_indicators: List[str] = Field(
        default_factory=list,
        description="Risk indicators identified"
    )
    
    def add_related_entity(self, entity_data: Dict[str, Any]) -> None:
        """Add a related entity."""
        self.related_entities.append(entity_data)
    
    def get_primary_pan(self) -> str:
        """Get primary entity PAN number."""
        return self.borrowing_entity.pan_number
    
    def get_primary_name(self) -> str:
        """Get primary entity name."""
        return self.borrowing_entity.entity_name
    
    @property
    def has_gst_registration(self) -> bool:
        """Check if entity has GST registration."""
        return self.borrowing_entity.gst_number is not None
    
    @property
    def has_udyam_registration(self) -> bool:
        """Check if entity has Udyam registration."""
        return self.borrowing_entity.udyam_number is not None
