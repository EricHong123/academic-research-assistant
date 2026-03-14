"""FastAPI application for Academic Research Assistant."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .routes import search, projects, chat, auth, export, briefings, parse
from ..utils.logging import logger, setup_logging
from ..utils.errors import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from ..utils.rate_limit import rate_limit_middleware
from ..utils.metrics import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging(level="INFO")
    logger.info("Starting Academic Research Assistant...")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Academic Research Assistant API",
    description="LangGraph-based AI agent for academic literature search and analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Apply rate limiting to requests."""
    return await rate_limit_middleware(request, call_next)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    response = await call_next(request)

    duration = (time.time() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {duration:.2f}ms",
        extra={
            "request": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            }
        },
    )

    return response


# Exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Include routers
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(parse.router, prefix="/api/parse", tags=["Parse"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(briefings.router, prefix="/api/briefings", tags=["Briefings"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Academic Research Assistant",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Basic health check."""
    return {"status": "healthy"}


@app.get("/health/deep")
async def deep_health():
    """Deep health check with component status."""
    health_status = {
        "status": "healthy",
        "components": {},
    }

    # Check database (mock for now)
    health_status["components"]["database"] = {"status": "healthy"}

    # Check Redis (mock for now)
    health_status["components"]["cache"] = {"status": "healthy"}

    # Check LLM (mock for now)
    health_status["components"]["llm"] = {"status": "healthy"}

    # Set overall status
    if any(c.get("status") != "healthy" for c in health_status["components"].values()):
        health_status["status"] = "degraded"

    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return registry.get_all()
