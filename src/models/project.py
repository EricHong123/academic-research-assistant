"""Project models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """Base project model."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation model."""

    pass


class Project(ProjectBase):
    """Project model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    paper_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectWithPapers(Project):
    """Project with papers."""

    papers: list[dict] = Field(default_factory=list)
