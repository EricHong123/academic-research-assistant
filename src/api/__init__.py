"""API routes for Academic Research Assistant."""
from .main import app
from .routes import search, projects, chat

__all__ = ["app", "search", "projects", "chat"]
