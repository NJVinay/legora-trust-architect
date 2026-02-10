"""
FastAPI dependencies for route-level security.

Provides:
  - API key verification (Req #5)
  - JWT bearer token verification (Req #9)
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.security import verify_token

logger = logging.getLogger(__name__)

# --- API Key Auth (Req #5) ---
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: Optional[str] = Security(_api_key_header),
) -> Optional[str]:
    """
    Verify the X-API-Key header against the configured API_KEY.

    If API_KEY is empty in settings (dev mode), authentication is skipped.
    In production, all requests without a valid key are rejected with 403.
    """
    settings = get_settings()

    # If no API key is configured, skip auth (dev mode)
    if not settings.API_KEY:
        return None

    if not api_key:
        logger.warning("Request rejected: missing X-API-Key header")
        raise HTTPException(
            status_code=403,
            detail="API key required",
        )

    if api_key != settings.API_KEY:
        logger.warning("Request rejected: invalid API key")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )

    return api_key


# --- JWT Bearer Auth (Req #9) ---
_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme),
) -> Optional[dict]:
    """
    Verify a JWT Bearer token from the Authorization header.

    Returns the decoded token payload if valid.
    If JWT_SECRET is the default unchanged value and DEBUG=True, auth is skipped.
    """
    settings = get_settings()

    # Skip JWT auth in dev mode with default secret
    if settings.DEBUG and settings.JWT_SECRET == "change-me-in-production":
        return {"sub": "dev-user", "type": "access"}

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    try:
        payload = verify_token(credentials.credentials, expected_type="access")
        return payload
    except Exception as e:
        logger.warning("JWT verification failed: %s", e)
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
