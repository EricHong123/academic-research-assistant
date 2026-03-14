"""Search models for academic literature queries."""
from typing import Optional
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Filters for search queries."""

    year_from: Optional[int] = Field(None, ge=1900, le=2030)
    year_to: Optional[int] = Field(None, ge=1900, le=2030)
    journal_tiers: list[str] = Field(
        default_factory=list, description="Q1, Q2, Q3, Q4"
    )
    paper_types: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    has_abstract: bool = True
    has_pdf: bool = False


class SearchQuery(BaseModel):
    """Search query model."""

    query: str = Field(..., description="Search query string with boolean operators")
    databases: list[str] = Field(
        default_factory=lambda: ["pubmed"],
        description="List of databases to search",
    )
    filters: SearchFilters = Field(default_factory=SearchFilters)
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class SearchResponse(BaseModel):
    """Response model for search results."""

    papers: list[dict] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    query: str
    databases_searched: list[str]


class QueryClassification(BaseModel):
    """Classification of a user query."""

    query_type: str = Field(..., description="search, parse, chat, or briefing")
    confidence: float = Field(ge=0, le=1)
    intent: Optional[str] = None
    entities: list[str] = Field(default_factory=list)
