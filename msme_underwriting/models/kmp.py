"""Models for Key Management Personnel (KMP) analysis."""

from typing import Dict, List, Optional, Any
from pydantic import Field

from .base import BaseModel


class ConstitutionRequirements(BaseModel):
    """Requirements based on entity constitution."""
    
    entity_type: str = Field(description="Type of entity")
    minimum_partners_required: Optional[int] = Field(default=None, description="Minimum partners required")
    maximum_partners_allowed: Optional[int] = Field(default=None, description="Maximum partners allowed")
    minimum_coverage_required: float = Field(description="Minimum coverage percentage required")
    required_documents: List[str] = Field(description="Required documents for this constitution")
    
    def get_coverage_requirement(self) -> float:
        """Get the minimum coverage requirement."""
        return self.minimum_coverage_required


class IdentifiedKMP(BaseModel):
    """Information about an identified Key Management Personnel."""
    
    kmp_id: str = Field(description="Unique KMP identifier")
    name: str = Field(description="KMP name")
    role: str = Field(description="Role in the entity (partner, director, etc.)")
    
    # Identity documents
    pan_number: Optional[str] = Field(default=None, description="PAN number")
    aadhaar_number: Optional[str] = Field(default=None, description="Aadhaar number")
    
    # Shareholding/Partnership details
    shareholding_percentage: Optional[float] = Field(default=None, description="Shareholding percentage")
    partnership_share: Optional[float] = Field(default=None, description="Partnership share")
    
    # Document availability
    documents_available: List[str] = Field(description="List of available documents")
    missing_documents: List[str] = Field(default_factory=list, description="List of missing documents")
    
    # API verification
    api_verified: bool = Field(default=False, description="Whether KMP is API verified")
    verified_name: Optional[str] = Field(default=None, description="API verified name")
    
    # Contact information
    address: Optional[Dict[str, str]] = Field(default=None, description="Address information")
    phone_number: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    
    # KYC status
    kyc_completeness: str = Field(description="KYC completeness status")
    kyc_score: Optional[float] = Field(default=None, description="KYC completeness score")
    
    # Risk assessment
    risk_flags: List[str] = Field(default_factory=list, description="Risk flags for this KMP")
    risk_score: Optional[float] = Field(default=None, description="Individual risk score")
    
    # Additional details
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")
    appointment_date: Optional[str] = Field(default=None, description="Date of appointment")
    
    @property
    def has_complete_kyc(self) -> bool:
        """Check if KMP has complete KYC."""
        return self.kyc_completeness == "complete"
    
    @property
    def effective_share(self) -> float:
        """Get effective shareholding/partnership share."""
        return self.shareholding_percentage or self.partnership_share or 0.0
    
    def get_missing_documents_for_kyc(self) -> List[str]:
        """Get documents missing for complete KYC."""
        required_docs = ["pan_card", "aadhaar_card"]
        available_docs = [doc.lower() for doc in self.documents_available]
        return [doc for doc in required_docs if doc not in available_docs]


class KMPCoverageAnalysis(BaseModel):
    """Analysis of KMP coverage."""
    
    total_partners_identified: int = Field(description="Total number of partners/directors identified")
    partners_with_complete_kyc: int = Field(description="Partners with complete KYC")
    partners_with_partial_kyc: int = Field(description="Partners with partial KYC")
    partners_with_no_kyc: int = Field(default=0, description="Partners with no KYC")
    
    total_shareholding_covered: float = Field(description="Total shareholding percentage covered")
    coverage_percentage: float = Field(description="Coverage percentage (0.0 to 1.0)")
    minimum_coverage_met: bool = Field(description="Whether minimum coverage is met")
    
    # Detailed breakdown
    coverage_by_kyc_status: Dict[str, float] = Field(
        default_factory=dict,
        description="Coverage breakdown by KYC status"
    )
    
    def calculate_coverage_metrics(self, kmps: List[IdentifiedKMP]) -> None:
        """Calculate coverage metrics from KMP list."""
        total_share = sum(kmp.effective_share for kmp in kmps)
        complete_kyc_share = sum(
            kmp.effective_share for kmp in kmps if kmp.has_complete_kyc
        )
        
        self.total_shareholding_covered = total_share
        self.coverage_percentage = complete_kyc_share / 100.0 if total_share > 0 else 0.0
        
        # Update counts
        self.partners_with_complete_kyc = sum(1 for kmp in kmps if kmp.has_complete_kyc)
        self.partners_with_partial_kyc = sum(
            1 for kmp in kmps 
            if not kmp.has_complete_kyc and len(kmp.documents_available) > 0
        )
        self.partners_with_no_kyc = sum(
            1 for kmp in kmps 
            if len(kmp.documents_available) == 0
        )


class KMPAnalysis(BaseModel):
    """Complete KMP analysis results."""
    
    constitution_requirements: ConstitutionRequirements = Field(
        description="Requirements based on entity constitution"
    )
    identified_kmps: List[IdentifiedKMP] = Field(description="List of identified KMPs")
    kmp_coverage_analysis: KMPCoverageAnalysis = Field(description="Coverage analysis")
    
    # Cross-validation results
    cross_validation_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cross-validation results across documents"
    )
    
    # Missing requirements
    missing_requirements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Missing KMP requirements"
    )
    
    # Data sources used
    data_sources_used: List[str] = Field(
        default_factory=list,
        description="Data sources used for KMP identification"
    )
    
    def get_kmp_by_id(self, kmp_id: str) -> Optional[IdentifiedKMP]:
        """Get KMP by ID."""
        for kmp in self.identified_kmps:
            if kmp.kmp_id == kmp_id:
                return kmp
        return None
    
    def get_kmps_by_role(self, role: str) -> List[IdentifiedKMP]:
        """Get KMPs by role."""
        return [kmp for kmp in self.identified_kmps if kmp.role.lower() == role.lower()]
    
    def get_kmps_with_complete_kyc(self) -> List[IdentifiedKMP]:
        """Get KMPs with complete KYC."""
        return [kmp for kmp in self.identified_kmps if kmp.has_complete_kyc]
    
    def get_kmps_missing_documents(self) -> List[IdentifiedKMP]:
        """Get KMPs with missing documents."""
        return [kmp for kmp in self.identified_kmps if len(kmp.missing_documents) > 0]
    
    def add_missing_requirement(self, requirement_type: str, missing_for: str, 
                              required_documents: List[str], shareholding_impact: float,
                              mandatory: bool, business_justification: str) -> None:
        """Add a missing requirement."""
        requirement = {
            "requirement_type": requirement_type,
            "missing_for": missing_for,
            "required_documents": required_documents,
            "shareholding_impact": shareholding_impact,
            "mandatory": mandatory,
            "business_justification": business_justification
        }
        self.missing_requirements.append(requirement)
    
    @property
    def total_identified_kmps(self) -> int:
        """Get total number of identified KMPs."""
        return len(self.identified_kmps)
    
    @property
    def meets_minimum_coverage(self) -> bool:
        """Check if minimum coverage requirement is met."""
        return self.kmp_coverage_analysis.minimum_coverage_met
    
    @property
    def coverage_percentage(self) -> float:
        """Get coverage percentage."""
        return self.kmp_coverage_analysis.coverage_percentage
    
    def calculate_risk_score(self) -> float:
        """Calculate overall KMP risk score."""
        if not self.identified_kmps:
            return 1.0  # High risk if no KMPs identified
        
        # Calculate based on coverage and individual risk scores
        coverage_score = self.coverage_percentage
        individual_risk_scores = [
            kmp.risk_score for kmp in self.identified_kmps 
            if kmp.risk_score is not None
        ]
        
        if individual_risk_scores:
            avg_individual_risk = sum(individual_risk_scores) / len(individual_risk_scores)
        else:
            avg_individual_risk = 0.5  # Neutral if no individual scores
        
        # Combine coverage and individual risk (weighted)
        overall_risk = (1 - coverage_score) * 0.6 + avg_individual_risk * 0.4
        return min(max(overall_risk, 0.0), 1.0)  # Clamp between 0 and 1
