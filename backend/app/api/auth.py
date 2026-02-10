"""
Authentication endpoints (Req #9).

Provides:
  - POST /api/auth/token  — issue access + refresh tokens
  - POST /api/auth/refresh — exchange refresh token for new access token

Uses stateless JWT tokens. Ready for database-backed user auth later.
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token, create_refresh_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    """Request body for token generation."""
    # In a real system, this would include username/password or OAuth code.
    # For now, it accepts an API key as a "credential" to issue JWT tokens.
    api_key: str


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """Request body for token refresh."""
    refresh_token: str


@router.post("/token", response_model=TokenResponse)
async def issue_token(request: TokenRequest):
    """
    Issue a JWT access token + refresh token.

    In production, this would validate user credentials against a database.
    Currently validates against the configured API_KEY.
    """
    from app.core.config import get_settings
    settings = get_settings()

    # Validate the API key as a credential
    if not settings.API_KEY or request.api_key != settings.API_KEY:
        logger.warning("Token request rejected: invalid API key")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": "api-user"}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    Exchange a valid refresh token for a new access token + refresh token.

    The old refresh token is consumed (single-use pattern).
    """
    from app.core.config import get_settings
    settings = get_settings()

    try:
        payload = verify_token(request.refresh_token, expected_type="refresh")
    except Exception as e:
        logger.warning("Refresh token rejected: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Issue new token pair
    token_data = {"sub": payload.get("sub", "api-user")}

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
