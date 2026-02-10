"""
API route definitions.

Security:
  - All routes require API key (Req #5)
  - Errors return generic messages to client (Req #4, #8)
  - Rate limiting on generate endpoints (Req #6)
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies import verify_api_key
from app.api.schemas import GenerateRequest, GenerateResponse
from app.core.config import get_settings
from app.models.constraints import (
    ContractConstraints,
    get_dpa_review_constraints,
    get_msa_review_constraints,
    get_privacy_review_constraints,
)
from app.services.ingestion import get_citation_index, get_document_metadata
from app.services.agent import run_agent_sync, run_agent_streaming

logger = logging.getLogger(__name__)

# All routes require API key auth
router = APIRouter(dependencies=[Depends(verify_api_key)])

# Rate limiter instance (attached to app state in main.py)
limiter = Limiter(key_func=get_remote_address)

# --- Preset mapping ---
PRESET_MAP = {
    "dpa": get_dpa_review_constraints,
    "msa": get_msa_review_constraints,
    "privacy": get_privacy_review_constraints,
}


@router.get("/citations")
async def get_citations():
    """Return all available source citations from ingested documents."""
    try:
        index = get_citation_index()
        return {"citations": index, "total": len(index)}
    except Exception as e:
        logger.exception("Failed to fetch citations")
        raise HTTPException(status_code=500, detail="Failed to retrieve citations")


@router.get("/citations/{source_id}")
async def get_citation(source_id: str):
    """Look up a single citation by SourceID."""
    try:
        from app.services.ingestion import get_citation as lookup
        citation = lookup(source_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return {
            "source_id": citation.source_id,
            "text": citation.text,
            "document_name": citation.document_name,
            "section_heading": citation.section_heading,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch citation %s", source_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve citation")


@router.get("/documents")
async def get_documents():
    """Return metadata about all ingested source documents."""
    try:
        metadata = get_document_metadata()
        return {"documents": metadata, "total": len(metadata)}
    except Exception as e:
        logger.exception("Failed to fetch documents")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")


@router.post("/generate", response_model=GenerateResponse)
@limiter.limit("10/minute")
async def generate(request: Request, body: GenerateRequest):
    """
    Generate and validate legal clauses (non-streaming).
    Rate-limited to 10 requests/minute.
    """
    constraints = _resolve_constraints(body)

    try:
        result = run_agent_sync(body.prompt, constraints)
    except Exception as e:
        logger.exception("Agent loop failed")
        raise HTTPException(status_code=500, detail="Generation failed. Please try again.")

    return GenerateResponse(
        success=result.success,
        total_attempts=result.total_attempts,
        output=result.output.model_dump() if result.output else None,
        validation=result.validation.model_dump() if result.validation else None,
        error=result.error_message,
    )


@router.post("/generate/stream")
@limiter.limit("10/minute")
async def generate_stream(request: Request, body: GenerateRequest):
    """
    Generate and validate legal clauses with SSE streaming.
    Rate-limited to 10 requests/minute.
    """
    constraints = _resolve_constraints(body)

    async def event_generator():
        try:
            async for event in run_agent_streaming(body.prompt, constraints):
                yield {
                    "event": event.state.value,
                    "data": json.dumps(event.to_dict()),
                }
        except Exception as e:
            logger.exception("Streaming agent loop failed")
            yield {
                "event": "error",
                "data": json.dumps({"state": "error", "message": "Generation failed"}),
            }

    return EventSourceResponse(event_generator())


@router.get("/constraints/presets")
async def get_presets():
    """Return available constraint presets for the frontend selector."""
    try:
        presets = {}
        for name, factory in PRESET_MAP.items():
            c = factory()
            presets[name] = {
                "contract_type": c.contract_type.value,
                "jurisdiction": c.governing_jurisdiction.value,
                "forbidden_clauses_count": len(c.forbidden_clauses),
                "required_citations_count": len(c.required_source_ids),
            }
        return {"presets": presets}
    except Exception as e:
        logger.exception("Failed to load presets")
        raise HTTPException(status_code=500, detail="Failed to load constraint presets")


def _resolve_constraints(request: GenerateRequest) -> ContractConstraints:
    """Resolve constraints from preset name or build from request params."""
    if request.preset and request.preset.lower() in PRESET_MAP:
        return PRESET_MAP[request.preset.lower()]()

    return ContractConstraints(
        contract_type=request.contract_type,
        governing_jurisdiction=request.jurisdiction,
    )
