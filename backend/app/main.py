"""
FastAPI application entry point.

Security features:
  - CORS locked to prod/dev domains only (Req #1)
  - Rate limiting via slowapi (Req #6)  
  - Global error handler returns generic messages (Req #4, #8)
  - API key auth on all /api routes (Req #5)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from app.services.ingestion import load_documents

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)

# --- Rate Limiter (Req #6) ---
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle events."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    try:
        load_documents()
        logger.info("Source documents loaded successfully")
    except Exception as e:
        logger.warning("Failed to load source documents: %s", e)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Neuro-Symbolic Legal Validation Agent — Trust-First Legal AI",
    lifespan=lifespan,
    # Hide docs in production (Req #5)
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Global Error Handlers (Req #4, #8) ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all: log full traceback server-side, return generic message to client.
    Never expose internal details in production.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred.",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic request validation errors — return generic message in prod.
    """
    logger.warning("Request validation error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid request",
            "detail": exc.errors() if settings.DEBUG else "The request body is invalid.",
        },
    )


# --- CORS Middleware (Req #1) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# --- Register Routes ---
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Simple health check endpoint — no auth required."""
    return {"status": "healthy", "version": settings.APP_VERSION}
