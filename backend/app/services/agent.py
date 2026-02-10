"""
Recursive Agent Loop — The Neuro-Symbolic Validation Engine.

This is the core orchestrator that implements:
    1. DRAFT:    LLM generates clause(s) based on context + constraints.
    2. VALIDATE: Deterministic code checks output against Pydantic schema.
    3. REFINE:   If validation fails, inject error context → LLM re-generates.
    
The loop emits state events for real-time frontend visualization.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Optional

from app.core.config import get_settings
from app.models.constraints import (
    AgentOutput,
    ContractConstraints,
    ValidationResult,
    ValidationViolation,
)
from app.services.llm_client import generate_structured_output
from app.services.validator import validate_output
from app.services.ingestion import get_citation_index, get_all_chunks

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#  Agent State Machine
# --------------------------------------------------------------------------- #

class AgentState(str, Enum):
    """States the agent transitions through, visible to the frontend."""
    INITIALIZING = "initializing"
    RETRIEVING = "retrieving"
    DRAFTING = "drafting"
    VALIDATING = "validating"
    VIOLATION_FOUND = "violation_found"
    CORRECTING = "correcting"
    FINALIZING = "finalizing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AgentEvent:
    """A state event emitted to the frontend for real-time visualization."""
    state: AgentState
    message: str
    data: Optional[dict] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentResult:
    """Final result of the agent loop."""
    output: Optional[AgentOutput]
    validation: ValidationResult
    events: list[AgentEvent]
    total_attempts: int
    success: bool
    error_message: Optional[str] = None


# --------------------------------------------------------------------------- #
#  Prompt Engineering
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT_TEMPLATE = """You are a Legal AI Assistant for Legora Trust-Architect.
Your task is to generate legally precise contract clauses based on the provided context and constraints.

CRITICAL RULES:
1. You MUST output valid JSON conforming to the schema below.
2. You MUST cite sources using the provided SourceIDs.
3. You MUST respect the governing jurisdiction: {jurisdiction}.
4. You MUST NOT include any forbidden clause patterns.
5. Each clause must be under {max_clause_length} words.
6. Set confidence_score based on how well your output matches the constraints.

OUTPUT JSON SCHEMA:
{{
    "clauses": [
        {{
            "title": "string - clause heading",
            "text": "string - the clause text",
            "citations": [{{"source_id": "string", "relevance": "string"}}],
            "risk_level": "low|medium|high|critical",
            "reasoning": "string - why you drafted it this way"
        }}
    ],
    "summary": "string - brief summary",
    "governing_jurisdiction": "{jurisdiction}",
    "confidence_score": 0.0-1.0
}}

CONSTRAINT PROFILE:
{constraints_json}

AVAILABLE SOURCE CONTEXT:
{source_context}
"""

RETRY_INJECTION_TEMPLATE = """
YOUR PREVIOUS ATTEMPT WAS REJECTED. You must fix the following violations:

{violation_summary}

SPECIFIC FIXES REQUIRED:
{fix_suggestions}

Generate a CORRECTED version that addresses ALL violations above.
Maintain the same JSON schema.
"""


def _build_system_prompt(
    constraints: ContractConstraints,
    source_context: str,
) -> str:
    """Build the system prompt with constraint profile and source context."""
    constraints_json = constraints.model_dump_json(indent=2)
    return SYSTEM_PROMPT_TEMPLATE.format(
        jurisdiction=constraints.governing_jurisdiction.value,
        max_clause_length=constraints.max_clause_length,
        constraints_json=constraints_json,
        source_context=source_context,
    )


def _build_retry_context(violations: list[ValidationViolation]) -> str:
    """Build the retry injection text from validation violations."""
    summary_lines = []
    fix_lines = []
    for v in violations:
        summary_lines.append(f"- [{v.severity.value.upper()}] {v.field}: {v.message}")
        if v.suggestion:
            fix_lines.append(f"- {v.suggestion}")

    return RETRY_INJECTION_TEMPLATE.format(
        violation_summary="\n".join(summary_lines),
        fix_suggestions="\n".join(fix_lines) if fix_lines else "Review and correct the violations.",
    )


def _get_relevant_context(constraints: ContractConstraints) -> str:
    """
    Retrieve relevant source context based on the contract type.
    
    For the demo, we include all chunks from the relevant document.
    In production, this would use FAISS vector similarity search.
    """
    chunks = get_all_chunks()

    # Map contract types to document prefixes
    type_to_prefix = {
        "Data Processing Agreement": "legora_dpa",
        "Privacy Policy": "legora_privacy",
        "Master Services Agreement": "zegal_msa",
        "Non-Disclosure Agreement": "legora_dpa",  # Fallback
        "Service Level Agreement": "zegal_msa",     # Fallback
    }

    target_prefix = type_to_prefix.get(
        constraints.contract_type.value,
        ""
    )

    relevant = [c for c in chunks if c.document_name == target_prefix]

    if not relevant:
        # Fallback: include all chunks
        relevant = chunks[:20]

    context_parts = []
    for chunk in relevant[:15]:  # Limit context window
        source_ids_str = ", ".join(chunk.source_ids) if chunk.source_ids else "N/A"
        context_parts.append(
            f"[Sources: {source_ids_str}]\n{chunk.text}\n"
        )

    return "\n---\n".join(context_parts)


# --------------------------------------------------------------------------- #
#  The Main Agent Loop
# --------------------------------------------------------------------------- #

def run_agent_sync(
    user_prompt: str,
    constraints: ContractConstraints,
) -> AgentResult:
    """
    Execute the recursive agent loop synchronously.
    
    Steps:
        1. Retrieve relevant source context
        2. Draft: LLM generates structured output
        3. Validate: Check against constraints
        4. If invalid: inject violations → retry (up to MAX_RETRIES)
        5. Return final result with full event log
    """
    settings = get_settings()
    max_retries = settings.MAX_VALIDATION_RETRIES
    events: list[AgentEvent] = []

    def emit(state: AgentState, message: str, data: dict = None):
        event = AgentEvent(state=state, message=message, data=data)
        events.append(event)
        logger.info("[Agent] %s: %s", state.value, message)

    # --- Step 1: Initialize ---
    emit(AgentState.INITIALIZING, "Starting legal analysis agent...")

    # --- Step 2: Retrieve Context ---
    emit(AgentState.RETRIEVING, "Retrieving relevant source documents...")
    try:
        source_context = _get_relevant_context(constraints)
        emit(
            AgentState.RETRIEVING,
            f"Retrieved context for {constraints.contract_type.value}",
            {"context_length": len(source_context)},
        )
    except Exception as e:
        emit(AgentState.ERROR, f"Failed to retrieve context: {e}")
        return AgentResult(
            output=None,
            validation=ValidationResult(is_valid=False, violations=[]),
            events=events,
            total_attempts=0,
            success=False,
            error_message=str(e),
        )

    # --- Step 3: Draft-Validate Loop ---
    system_prompt = _build_system_prompt(constraints, source_context)
    current_prompt = user_prompt
    last_output: Optional[AgentOutput] = None
    last_validation: Optional[ValidationResult] = None

    for attempt in range(1, max_retries + 1):
        # Draft
        emit(
            AgentState.DRAFTING,
            f"Generating draft (attempt {attempt}/{max_retries})...",
            {"attempt": attempt},
        )

        try:
            output = generate_structured_output(system_prompt, current_prompt)
            last_output = output
            emit(
                AgentState.DRAFTING,
                f"Draft generated: {len(output.clauses)} clause(s), "
                f"confidence {output.confidence_score:.0%}",
                {"clauses_count": len(output.clauses), "confidence": output.confidence_score},
            )
        except ValueError as e:
            emit(AgentState.ERROR, f"LLM output error: {e}")
            if attempt < max_retries:
                current_prompt = (
                    user_prompt
                    + f"\n\nPREVIOUS ATTEMPT FAILED: {e}\nPlease fix and try again."
                )
                continue
            else:
                return AgentResult(
                    output=None,
                    validation=ValidationResult(is_valid=False, violations=[]),
                    events=events,
                    total_attempts=attempt,
                    success=False,
                    error_message=str(e),
                )

        # Validate
        emit(AgentState.VALIDATING, "Running constraint validation...")
        validation = validate_output(output, constraints)
        validation.attempt_number = attempt
        last_validation = validation

        if validation.is_valid:
            emit(
                AgentState.FINALIZING,
                "✅ All constraints satisfied!",
                {"attempt": attempt},
            )
            emit(AgentState.COMPLETE, "Agent loop complete — output verified.")
            return AgentResult(
                output=output,
                validation=validation,
                events=events,
                total_attempts=attempt,
                success=True,
            )

        # Violation found — prepare retry
        emit(
            AgentState.VIOLATION_FOUND,
            f"❌ {len(validation.violations)} violation(s) found",
            {
                "violations": [
                    {"field": v.field, "message": v.message, "severity": v.severity.value}
                    for v in validation.violations
                ],
            },
        )

        if attempt < max_retries:
            emit(
                AgentState.CORRECTING,
                f"Injecting corrections for retry {attempt + 1}...",
            )
            retry_context = _build_retry_context(validation.violations)
            current_prompt = user_prompt + retry_context
        else:
            emit(
                AgentState.ERROR,
                f"Max retries ({max_retries}) exhausted. Returning best effort.",
            )

    # Exhausted retries — return last attempt
    return AgentResult(
        output=last_output,
        validation=last_validation or ValidationResult(is_valid=False, violations=[]),
        events=events,
        total_attempts=max_retries,
        success=False,
        error_message=f"Validation failed after {max_retries} attempts.",
    )


# --------------------------------------------------------------------------- #
#  Streaming Event Generator (for SSE)
# --------------------------------------------------------------------------- #

async def run_agent_streaming(
    user_prompt: str,
    constraints: ContractConstraints,
) -> AsyncGenerator[AgentEvent, None]:
    """
    Async generator that yields AgentEvents as they happen.
    
    This powers the SSE endpoint for real-time frontend visualization.
    The actual LLM calls are synchronous (wrapped in a thread),
    but the event emission is async for streaming.
    """
    import asyncio

    # Run the sync agent in a thread pool (Req #6: proper async)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        run_agent_sync,
        user_prompt,
        constraints,
    )

    # Yield all events (sanitize error messages for client)
    for event in result.events:
        if event.state == AgentState.ERROR:
            # Don't leak internal error details to client
            event = AgentEvent(
                state=event.state,
                message="An error occurred during processing",
                data=None,
                timestamp=event.timestamp,
            )
        yield event

    # Final event with the complete result
    if result.success and result.output:
        yield AgentEvent(
            state=AgentState.COMPLETE,
            message="Generation complete",
            data={
                "output": result.output.model_dump(),
                "validation": result.validation.model_dump(),
                "total_attempts": result.total_attempts,
            },
        )
    else:
        yield AgentEvent(
            state=AgentState.ERROR,
            message="Generation could not be completed",
            data={
                "validation": result.validation.model_dump() if result.validation else None,
                "total_attempts": result.total_attempts,
            },
        )
