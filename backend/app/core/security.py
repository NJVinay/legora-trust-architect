"""
Core security utilities.

Provides:
  - Redirect URL validation (Req #2)
  - Storage policies with per-user file isolation (Req #3)
  - JWT token creation/verification (Req #9)
  - Filename sanitization
"""

import logging
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

import jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#  Redirect URL Validation (Req #2)
# --------------------------------------------------------------------------- #

def validate_redirect_url(url: str) -> bool:
    """
    Validate that a redirect URL points to an allowed domain.

    Returns True if the URL is safe to redirect to, False otherwise.
    Currently no redirects exist in the app — this is a safety net for
    when they are added.
    """
    settings = get_settings()

    try:
        parsed = urlparse(url)
    except Exception:
        logger.warning("Failed to parse redirect URL: %s", url)
        return False

    # Allow relative URLs (same-origin)
    if not parsed.scheme and not parsed.netloc:
        return True

    # Reject non-HTTP(S) schemes (javascript:, data:, etc.)
    if parsed.scheme not in ("http", "https"):
        logger.warning("Rejected non-HTTP redirect scheme: %s", parsed.scheme)
        return False

    # Check against allowlist
    hostname = parsed.hostname or ""
    for allowed in settings.ALLOWED_REDIRECT_DOMAINS:
        if hostname == allowed or hostname.endswith(f".{allowed}"):
            return True

    logger.warning("Rejected redirect to unlisted domain: %s", hostname)
    return False


def get_safe_redirect_url(url: str, fallback: str = "/") -> str:
    """Return the URL if allowed, otherwise return the fallback."""
    return url if validate_redirect_url(url) else fallback


# --------------------------------------------------------------------------- #
#  Storage Policies (Req #3)
# --------------------------------------------------------------------------- #

# Matches any path traversal attempts: ../, ..\, etc.
_PATH_TRAVERSAL_PATTERN = re.compile(r"\.\.[/\\]")

# Only allow safe filename characters
_SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-][a-zA-Z0-9_.\-]*$")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and injection attacks.

    Raises ValueError if the filename is invalid or dangerous.
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")

    # Strip path separators
    clean = filename.replace("/", "").replace("\\", "").strip()

    # Reject path traversal
    if _PATH_TRAVERSAL_PATTERN.search(filename):
        raise ValueError("Path traversal detected in filename")

    # Reject unsafe characters
    if not _SAFE_FILENAME_PATTERN.match(clean):
        raise ValueError(f"Unsafe filename characters: {clean}")

    # Check extension
    settings = get_settings()
    ext = "." + clean.rsplit(".", 1)[-1].lower() if "." in clean else ""
    if ext and ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise ValueError(f"File extension '{ext}' not allowed")

    return clean


def get_user_storage_path(user_id: str) -> str:
    """
    Get the isolated storage path for a user.

    Ensures users can only access files they uploaded.
    Ready for integration when a database/upload system is added.
    """
    # Sanitize user_id to prevent traversal
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", user_id)
    if not safe_id:
        raise ValueError("Invalid user ID for storage path")
    return f"uploads/{safe_id}"


def validate_file_access(user_id: str, file_path: str) -> bool:
    """
    Validates that a user is only accessing files within their own storage.

    Returns True if access is allowed, False otherwise.
    """
    expected_prefix = get_user_storage_path(user_id)
    normalized = file_path.replace("\\", "/")

    if _PATH_TRAVERSAL_PATTERN.search(normalized):
        logger.warning("Path traversal attempt by user %s: %s", user_id, file_path)
        return False

    if not normalized.startswith(expected_prefix):
        logger.warning(
            "User %s attempted to access file outside their storage: %s",
            user_id,
            file_path,
        )
        return False

    return True


# --------------------------------------------------------------------------- #
#  JWT Token Management (Req #9)
# --------------------------------------------------------------------------- #

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a short-lived JWT access token."""
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token."""
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_hex(16),  # unique token ID for revocation
    })

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verify and decode a JWT token.

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
        ValueError: Token type mismatch
    """
    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )

    if payload.get("type") != expected_type:
        raise ValueError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")

    return payload
