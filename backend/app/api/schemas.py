"""
API Request/Response models.
"""

from pydantic import BaseModel, Field
from typing import Optional

from app.models.constraints import ContractType, Jurisdiction


class GenerateRequest(BaseModel):
    """Request body for the /generate endpoint."""

    prompt: str = Field(
        ...,
        min_length=10,
        description="The user's natural language request (e.g., 'Review this DPA for GDPR compliance')."
    )
    contract_type: ContractType = Field(
        ContractType.DPA,
        description="Type of contract to generate/review."
    )
    jurisdiction: Jurisdiction = Field(
        Jurisdiction.EU,
        description="Governing jurisdiction."
    )
    preset: Optional[str] = Field(
        None,
        description="Use a preset constraint profile: 'dpa', 'msa', or 'privacy'."
    )


class GenerateResponse(BaseModel):
    """Non-streaming response from the /generate endpoint."""

    success: bool
    total_attempts: int
    output: Optional[dict] = None
    validation: Optional[dict] = None
    error: Optional[str] = None
