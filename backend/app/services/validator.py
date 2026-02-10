"""
Constraint Validator Service.

Performs deterministic validation of LLM-generated output against the
ContractConstraints profile. This is the "code" half of Neuro-Symbolic Validation.

Flow:
    AgentOutput (from LLM) + ContractConstraints (from Client) → ValidationResult
"""

import re
import logging
from app.models.constraints import (
    AgentOutput,
    ContractConstraints,
    ValidationResult,
    ValidationViolation,
    RiskLevel,
    GeneratedClause,
)

logger = logging.getLogger(__name__)


def validate_output(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> ValidationResult:
    """
    Validate LLM output against all constraint rules.
    
    Returns a ValidationResult with is_valid=True if all checks pass,
    or a list of violations if any fail.
    """
    violations: list[ValidationViolation] = []

    # 1. Jurisdiction check
    violations.extend(_check_jurisdiction(output, constraints))

    # 2. Forbidden clause check
    violations.extend(_check_forbidden_clauses(output, constraints))

    # 3. Required citations check
    violations.extend(_check_required_citations(output, constraints))

    # 4. Liability constraints check
    violations.extend(_check_liability(output, constraints))

    # 5. Data protection constraints check
    violations.extend(_check_data_protection(output, constraints))

    # 6. Clause length check
    violations.extend(_check_clause_length(output, constraints))

    is_valid = len(violations) == 0

    result = ValidationResult(
        is_valid=is_valid,
        violations=violations,
    )

    if not is_valid:
        logger.warning(
            "Validation FAILED with %d violation(s):\n%s",
            len(violations),
            result.violation_summary,
        )
    else:
        logger.info("Validation PASSED — all constraints satisfied.")

    return result


# --------------------------------------------------------------------------- #
#  Individual Validation Checks
# --------------------------------------------------------------------------- #

def _check_jurisdiction(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Verify the output specifies the correct governing jurisdiction."""
    violations = []
    if output.governing_jurisdiction != constraints.governing_jurisdiction:
        violations.append(ValidationViolation(
            field="governing_jurisdiction",
            message=(
                f"Expected jurisdiction '{constraints.governing_jurisdiction.value}' "
                f"but got '{output.governing_jurisdiction.value}'."
            ),
            severity=RiskLevel.HIGH,
            suggestion=(
                f"Change the governing jurisdiction to "
                f"'{constraints.governing_jurisdiction.value}'."
            ),
        ))
    return violations


def _check_forbidden_clauses(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Check that no forbidden clause patterns appear in the generated text."""
    violations = []
    full_text = _get_full_text(output)

    for forbidden in constraints.forbidden_clauses:
        if re.search(forbidden.pattern, full_text):
            violations.append(ValidationViolation(
                field="forbidden_clause",
                message=(
                    f"Forbidden pattern detected: '{forbidden.pattern}'. "
                    f"Reason: {forbidden.reason}"
                ),
                severity=forbidden.severity,
                suggestion=f"Remove or rephrase any language matching: {forbidden.pattern}",
            ))

    return violations


def _check_required_citations(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Verify that required SourceIDs are cited in the output."""
    violations = []

    if not constraints.required_source_ids:
        return violations

    cited_ids = set()
    for clause in output.clauses:
        for citation in clause.citations:
            cited_ids.add(citation.source_id)

    for required_id in constraints.required_source_ids:
        if required_id not in cited_ids:
            violations.append(ValidationViolation(
                field="required_citations",
                message=f"Required citation '{required_id}' is missing from the output.",
                severity=RiskLevel.MEDIUM,
                suggestion=f"Include a citation to [SourceID: {required_id}] in your response.",
            ))

    return violations


def _check_liability(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Check liability-related constraints against the generated text."""
    violations = []
    full_text = _get_full_text(output).lower()

    liability = constraints.liability

    # Check for unlimited liability if not allowed
    if not liability.allows_unlimited_liability:
        if re.search(r"unlimited\s+liability", full_text):
            violations.append(ValidationViolation(
                field="liability.unlimited",
                message="Output contains 'unlimited liability' but this is not permitted.",
                severity=RiskLevel.CRITICAL,
                suggestion="Replace unlimited liability with a capped liability clause.",
            ))

    # Check for consequential damages if not allowed
    if not liability.allows_consequential_damages:
        if re.search(r"consequential\s+damages?\b", full_text):
            violations.append(ValidationViolation(
                field="liability.consequential_damages",
                message="Output mentions 'consequential damages' but these are excluded by the constraint profile.",
                severity=RiskLevel.HIGH,
                suggestion="Add exclusion language for consequential and indirect damages.",
            ))

    return violations


def _check_data_protection(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Check data protection constraints."""
    violations = []
    full_text = _get_full_text(output).lower()
    dp = constraints.data_protection

    # GDPR compliance check
    if dp.requires_gdpr_compliance:
        if "gdpr" not in full_text and "general data protection" not in full_text:
            violations.append(ValidationViolation(
                field="data_protection.gdpr",
                message="GDPR compliance is required but no GDPR reference found in output.",
                severity=RiskLevel.HIGH,
                suggestion="Include explicit reference to GDPR compliance.",
            ))

    # Breach notification check
    if dp.requires_breach_notification:
        if "breach" not in full_text and "notification" not in full_text:
            violations.append(ValidationViolation(
                field="data_protection.breach_notification",
                message="Breach notification clause is required but not found.",
                severity=RiskLevel.HIGH,
                suggestion=(
                    f"Include a breach notification clause with a "
                    f"{dp.max_breach_notification_hours}-hour notification window."
                ),
            ))

    return violations


def _check_clause_length(
    output: AgentOutput,
    constraints: ContractConstraints,
) -> list[ValidationViolation]:
    """Check that individual clauses don't exceed the word limit."""
    violations = []

    for clause in output.clauses:
        word_count = len(clause.text.split())
        if word_count > constraints.max_clause_length:
            violations.append(ValidationViolation(
                field=f"clause_length.{clause.title}",
                message=(
                    f"Clause '{clause.title}' has {word_count} words, "
                    f"exceeding the limit of {constraints.max_clause_length}."
                ),
                severity=RiskLevel.LOW,
                suggestion=f"Shorten this clause to under {constraints.max_clause_length} words.",
            ))

    return violations


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _get_full_text(output: AgentOutput) -> str:
    """Concatenate all clause text for full-text analysis."""
    return " ".join(clause.text for clause in output.clauses)
