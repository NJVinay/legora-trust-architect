"""
Pydantic Constraint Models — The "Client Playbook".

These models define deterministic legal rules that LLM-generated clauses
must satisfy. They act as the validation layer in the Neuro-Symbolic pipeline:

    LLM Draft → Pydantic Validation → Pass/Fail → Retry if Fail

Each model represents a specific contract scenario with hard constraints
that cannot be violated (liability caps, jurisdiction, forbidden terms, etc.)
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import re


# --------------------------------------------------------------------------- #
#  Enums
# --------------------------------------------------------------------------- #

class Jurisdiction(str, Enum):
    """Supported governing law jurisdictions."""
    SWEDEN = "Sweden"
    EU = "European Union"
    UK = "United Kingdom"
    US_CALIFORNIA = "California, USA"
    US_DELAWARE = "Delaware, USA"
    US_NEW_YORK = "New York, USA"


class ContractType(str, Enum):
    """Types of contracts the system can validate."""
    NDA = "Non-Disclosure Agreement"
    MSA = "Master Services Agreement"
    DPA = "Data Processing Agreement"
    PRIVACY_POLICY = "Privacy Policy"
    SLA = "Service Level Agreement"


class RiskLevel(str, Enum):
    """Risk classification for generated clauses."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# --------------------------------------------------------------------------- #
#  Constraint Models
# --------------------------------------------------------------------------- #

class LiabilityConstraints(BaseModel):
    """Hard limits on liability language in generated clauses."""

    max_liability_amount: Optional[float] = Field(
        None,
        description="Maximum liability cap in USD. None means uncapped (dangerous)."
    )
    liability_cap_multiple_of_fees: Optional[float] = Field(
        None,
        description="Liability cap as a multiple of annual fees (e.g., 2.0 = 2x fees)."
    )
    allows_consequential_damages: bool = Field(
        False,
        description="Whether consequential/indirect damages are permitted."
    )
    allows_unlimited_liability: bool = Field(
        False,
        description="Whether unlimited liability is acceptable."
    )

    @model_validator(mode="after")
    def validate_liability_cap(self) -> LiabilityConstraints:
        """At least one cap mechanism should be defined."""
        if (self.max_liability_amount is None
            and self.liability_cap_multiple_of_fees is None
            and not self.allows_unlimited_liability):
            raise ValueError(
                "A liability cap must be defined: either max_liability_amount, "
                "liability_cap_multiple_of_fees, or allows_unlimited_liability=True"
            )
        return self


class DataProtectionConstraints(BaseModel):
    """Constraints for data handling and privacy compliance."""

    required_jurisdiction: Jurisdiction = Field(
        Jurisdiction.EU,
        description="Required governing law for data protection."
    )
    requires_gdpr_compliance: bool = Field(
        True,
        description="Whether GDPR compliance language is mandatory."
    )
    max_data_retention_days: Optional[int] = Field(
        None,
        description="Maximum data retention period in days."
    )
    requires_breach_notification: bool = Field(
        True,
        description="Whether breach notification clause is required."
    )
    max_breach_notification_hours: int = Field(
        72,
        description="Maximum hours allowed for breach notification."
    )
    allows_cross_border_transfer: bool = Field(
        True,
        description="Whether cross-border data transfers are permitted."
    )
    requires_sub_processor_approval: bool = Field(
        True,
        description="Whether subscriber approval for sub-processors is required."
    )


class TerminationConstraints(BaseModel):
    """Constraints on termination clauses."""

    min_notice_period_days: int = Field(
        30,
        description="Minimum notice period for termination in days."
    )
    allows_termination_for_convenience: bool = Field(
        True,
        description="Whether either party can terminate without cause."
    )
    requires_data_return_on_termination: bool = Field(
        True,
        description="Whether data must be returned/deleted upon termination."
    )


class ForbiddenClause(BaseModel):
    """A specific clause pattern that must NOT appear in generated text."""

    pattern: str = Field(
        ...,
        description="Regex pattern or keyword that is forbidden."
    )
    reason: str = Field(
        ...,
        description="Why this clause is forbidden."
    )
    severity: RiskLevel = Field(
        RiskLevel.HIGH,
        description="How severe a violation this represents."
    )


# --------------------------------------------------------------------------- #
#  The Master Constraint Profile — "Client Playbook"
# --------------------------------------------------------------------------- #

class ContractConstraints(BaseModel):
    """
    The complete constraint profile for a contract generation request.
    This is the Pydantic model that validates LLM output.
    """

    contract_type: ContractType = Field(
        ...,
        description="Type of contract being generated."
    )
    governing_jurisdiction: Jurisdiction = Field(
        Jurisdiction.SWEDEN,
        description="Governing law jurisdiction."
    )
    liability: LiabilityConstraints = Field(
        default_factory=lambda: LiabilityConstraints(
            liability_cap_multiple_of_fees=2.0,
            allows_consequential_damages=False,
        )
    )
    data_protection: DataProtectionConstraints = Field(
        default_factory=DataProtectionConstraints
    )
    termination: TerminationConstraints = Field(
        default_factory=TerminationConstraints
    )
    forbidden_clauses: list[ForbiddenClause] = Field(
        default_factory=list,
        description="List of clause patterns that must NOT appear."
    )
    required_source_ids: list[str] = Field(
        default_factory=list,
        description="SourceIDs that MUST be cited in the output."
    )
    max_clause_length: int = Field(
        500,
        description="Maximum word count for a single generated clause."
    )


# --------------------------------------------------------------------------- #
#  LLM Output Schema — What the LLM must return
# --------------------------------------------------------------------------- #

class GeneratedCitation(BaseModel):
    """A citation reference in the generated output."""
    source_id: str = Field(..., description="The SourceID being cited.")
    relevance: str = Field(..., description="Why this source is relevant.")


class GeneratedClause(BaseModel):
    """A single clause generated by the LLM, ready for validation."""

    title: str = Field(
        ...,
        description="Heading/title for this clause."
    )
    text: str = Field(
        ...,
        description="The actual clause text."
    )
    citations: list[GeneratedCitation] = Field(
        default_factory=list,
        description="Source citations supporting this clause."
    )
    risk_level: RiskLevel = Field(
        RiskLevel.LOW,
        description="Risk assessment of this clause."
    )
    reasoning: str = Field(
        "",
        description="LLM's reasoning for drafting this clause."
    )

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Clause text cannot be empty.")
        return v.strip()


class AgentOutput(BaseModel):
    """Complete structured output from the LLM agent."""

    clauses: list[GeneratedClause] = Field(
        ...,
        min_length=1,
        description="Generated clauses."
    )
    summary: str = Field(
        ...,
        description="Brief summary of what was generated."
    )
    governing_jurisdiction: Jurisdiction = Field(
        ...,
        description="The jurisdiction applied."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Agent's confidence in the output (0-1)."
    )


# --------------------------------------------------------------------------- #
#  Validation Result
# --------------------------------------------------------------------------- #

class ValidationViolation(BaseModel):
    """A single violation found during constraint validation."""

    field: str = Field(..., description="Which constraint was violated.")
    message: str = Field(..., description="Human-readable violation description.")
    severity: RiskLevel = Field(..., description="Severity of the violation.")
    suggestion: str = Field("", description="Suggested fix for the LLM.")


class ValidationResult(BaseModel):
    """Result of validating LLM output against constraints."""

    is_valid: bool = Field(..., description="Whether the output passes all constraints.")
    violations: list[ValidationViolation] = Field(default_factory=list)
    attempt_number: int = Field(1, description="Which attempt this is (1-based).")

    @property
    def violation_summary(self) -> str:
        """Human-readable summary of all violations."""
        if self.is_valid:
            return "No violations found."
        lines = [f"Found {len(self.violations)} violation(s):"]
        for v in self.violations:
            lines.append(f"  [{v.severity.value.upper()}] {v.field}: {v.message}")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Preset Profiles — Demo-Ready Constraint Sets
# --------------------------------------------------------------------------- #

def get_dpa_review_constraints() -> ContractConstraints:
    """Preset constraints for reviewing a Data Processing Agreement."""
    return ContractConstraints(
        contract_type=ContractType.DPA,
        governing_jurisdiction=Jurisdiction.EU,
        liability=LiabilityConstraints(
            liability_cap_multiple_of_fees=2.0,
            allows_consequential_damages=False,
        ),
        data_protection=DataProtectionConstraints(
            required_jurisdiction=Jurisdiction.EU,
            requires_gdpr_compliance=True,
            max_breach_notification_hours=36,
            requires_sub_processor_approval=True,
        ),
        termination=TerminationConstraints(
            min_notice_period_days=30,
            requires_data_return_on_termination=True,
        ),
        forbidden_clauses=[
            ForbiddenClause(
                pattern=r"(?i)unlimited\s+liability",
                reason="Unlimited liability is never acceptable in DPAs.",
                severity=RiskLevel.CRITICAL,
            ),
            ForbiddenClause(
                pattern=r"(?i)waive.*right.*to.*audit",
                reason="Audit rights cannot be waived under GDPR.",
                severity=RiskLevel.CRITICAL,
            ),
            ForbiddenClause(
                pattern=r"(?i)sell.*personal\s+data",
                reason="Selling personal data is prohibited.",
                severity=RiskLevel.CRITICAL,
            ),
        ],
        required_source_ids=["DPA-7.1", "DPA-6.2", "DPA-9.1"],
    )


def get_msa_review_constraints() -> ContractConstraints:
    """Preset constraints for reviewing a Master Services Agreement."""
    return ContractConstraints(
        contract_type=ContractType.MSA,
        governing_jurisdiction=Jurisdiction.SWEDEN,
        liability=LiabilityConstraints(
            max_liability_amount=1_000_000,
            allows_consequential_damages=False,
        ),
        data_protection=DataProtectionConstraints(
            requires_gdpr_compliance=True,
        ),
        termination=TerminationConstraints(
            min_notice_period_days=60,
            allows_termination_for_convenience=True,
        ),
        forbidden_clauses=[
            ForbiddenClause(
                pattern=r"(?i)non-?compete",
                reason="Non-compete clauses are not acceptable in this MSA.",
                severity=RiskLevel.HIGH,
            ),
            ForbiddenClause(
                pattern=r"(?i)automatic\s+renewal",
                reason="Auto-renewal without explicit consent is risky.",
                severity=RiskLevel.MEDIUM,
            ),
        ],
    )


def get_privacy_review_constraints() -> ContractConstraints:
    """Preset constraints for reviewing a Privacy Policy."""
    return ContractConstraints(
        contract_type=ContractType.PRIVACY_POLICY,
        governing_jurisdiction=Jurisdiction.EU,
        liability=LiabilityConstraints(
            allows_unlimited_liability=True,  # Not applicable for privacy policies
        ),
        data_protection=DataProtectionConstraints(
            required_jurisdiction=Jurisdiction.EU,
            requires_gdpr_compliance=True,
            max_data_retention_days=365 * 7,  # 7 years max
            max_breach_notification_hours=72,
        ),
        forbidden_clauses=[
            ForbiddenClause(
                pattern=r"(?i)sell.*your.*data",
                reason="Claiming to sell user data violates GDPR principles.",
                severity=RiskLevel.CRITICAL,
            ),
        ],
        required_source_ids=["Priv-4.1", "Priv-6.1"],
    )
