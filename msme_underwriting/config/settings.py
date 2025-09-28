"""Application settings and configuration."""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    environment: str = Field(default="development", description="Environment (development/staging/production)")
    log_level: str = Field(default="INFO", description="Logging level")
    max_concurrent_agents: int = Field(default=5, description="Maximum concurrent agents")
    agent_timeout_seconds: int = Field(default=300, description="Agent timeout in seconds")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    default_model: str = Field(default="gpt-4o", description="Default model name")
    
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/msme_underwriting")
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # External APIs
    pan_api_key: Optional[str] = Field(default=None, description="PAN validation API key")
    mca_api_key: Optional[str] = Field(default=None, description="MCA API key")
    cibil_api_key: Optional[str] = Field(default=None, description="CIBIL API key")
    gst_api_key: Optional[str] = Field(default=None, description="GST API key")
    
    # Document Processing Service
    document_processing_service_url: str = Field(
        default="http://localhost:8001", 
        description="PDF/Image processing service URL"
    )
    document_processing_api_key: Optional[str] = Field(
        default=None, 
        description="Document processing service API key"
    )
    
    # File Storage
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    
    # Security
    secret_key: str = Field(default="your_secret_key_here", description="Application secret key")
    jwt_secret: str = Field(default="your_jwt_secret_here", description="JWT secret key")
    
    # Monitoring and Tracing
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langsmith_project: str = Field(default="msme-underwriting", description="LangSmith project name")
    langsmith_tracing: bool = Field(default=True, description="Enable LangSmith tracing")
    
    # Business Rules
    minimum_kmp_coverage: float = Field(default=0.5, description="Minimum KMP coverage percentage")
    minimum_consumer_cibil: int = Field(default=680, description="Minimum consumer CIBIL score")
    maximum_commercial_cmr: int = Field(default=8, description="Maximum commercial CMR score")
    minimum_commercial_score: int = Field(default=1, description="Minimum commercial score")
    
    # Eligible constitutions for MSME loans
    eligible_constitutions: List[str] = Field(
        default=["sole_proprietorship", "partnership", "llp", "company", "huf"],
        description="Eligible entity constitutions"
    )
    
    # Document confidence thresholds
    minimum_document_confidence: float = Field(default=0.7, description="Minimum document confidence score")
    high_confidence_threshold: float = Field(default=0.9, description="High confidence threshold")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
