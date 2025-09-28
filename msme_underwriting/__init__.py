"""
MSME Loan Processing Agent Architecture using LangGraph

This package implements a comprehensive multi-agent system for MSME loan underwriting
using LangGraph orchestration. The system processes loan applications through a series
of specialized agents that handle document classification, entity identification,
verification, financial analysis, and final report generation.

Architecture:
- Agent 1: Document Classification & Extraction
- Agent 2: Entity & KMP Identification  
- Agent 3: Verification & Compliance
- Agent 4: Financial Analysis
- Agent 7: Banking Analysis
- Agent 6: Final Assembly & Report Generation
- Agent 5: Relationship Mapping (Phase 2)

The system integrates with external APIs for PAN validation, bureau checks, GST analysis,
and document processing services.
"""

__version__ = "0.1.0"
__author__ = "Development Team"
__email__ = "dev@company.com"

from .config import settings
from .models import *
from .agents import *
from .services import *

__all__ = [
    "settings",
    # Models will be imported from models module
    # Agents will be imported from agents module  
    # Services will be imported from services module
]
