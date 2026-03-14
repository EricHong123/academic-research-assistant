"""Paper models for academic literature."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PaperMetadata(BaseModel):
    """Metadata for a paper from academic databases."""

    doi: Optional[str] = None
    pmid: Optional[str] = None
    issn: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    citation_count: Optional[int] = None
    impact_factor: Optional[float] = None
    quartile: Optional[str] = Field(None, description="Q1, Q2, Q3, or Q4")


class Paper(BaseModel):
    """Core paper model."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    year: Optional[int] = None
    source: str = Field(..., description="wos, scopus, pubmed, google_scholar, etc.")
    paper_type: Optional[str] = Field(None, description="research_type, review, meta_analysis")
    pdf_url: Optional[str] = None
    url: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    metadata: PaperMetadata = Field(default_factory=PaperMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaperSearchResult(BaseModel):
    """Search result for a paper with ranking score."""

    paper: Paper
    score: float = Field(ge=0, le=1)
    relevance_breakdown: Optional[dict[str, float]] = None


class ParsedPaperData(BaseModel):
    """Parsed structured data from a paper."""

    research_type: Optional[str] = Field(None, description="横断面/纵向/荟萃分析/实验")
    independent_vars: list[str] = Field(default_factory=list)
    dependent_vars: list[str] = Field(default_factory=list)
    mediating_vars: list[str] = Field(default_factory=list)
    moderating_vars: list[str] = Field(default_factory=list)
    sample_size: Optional[int] = None
    subjects: list[str] = Field(default_factory=list)
    instruments: list[dict[str, str]] = Field(
        default_factory=list, description="List of scales/measurements used"
    )
    key_findings: Optional[str] = None
    limitations: list[str] = Field(default_factory=list)
    future_directions: list[str] = Field(default_factory=list)
    statistical_values: list[dict[str, str]] = Field(
        default_factory=list, description="Extracted statistical values (r, d, F, t, p)"
    )
    raw_json: dict = Field(default_factory=dict)
