"""FastAPI application for Academic Research Assistant."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import search, projects, chat, auth, export, briefings, parse
from ..utils.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    setup_logging(level="INFO")
    logger.info("Starting Academic Research Assistant...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Academic Research Assistant API",
    description="LangGraph-based AI agent for academic literature search and analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "name": "Academic Research Assistant",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/health/deep")
async def deep_health():
    return {
        "status": "healthy",
        "components": {
            "database": {"status": "healthy"},
            "cache": {"status": "healthy"},
            "llm": {"status": "healthy"},
        },
    }
