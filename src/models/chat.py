"""Chat models for RAG conversations."""
from typing import Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation for a source."""

    paper_id: str
    authors: str
    year: int
    page: Optional[str] = None
    text: str = Field(..., description="The cited text from the source")


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="user or assistant")
    content: str
    citations: list[Citation] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Chat request model."""

    project_id: str
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""

    message: ChatMessage
    conversation_id: str
    references: list[dict] = Field(default_factory=list)
