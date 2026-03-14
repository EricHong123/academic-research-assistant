"""Projects API routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...models.project import Project, ProjectCreate


router = APIRouter()


# In-memory storage (replace with database in production)
_projects_db: dict[str, dict] = {}


def get_current_user_id() -> str:
    """Get current user ID (replace with auth)."""
    return "demo-user"


@router.post("", response_model=dict)
async def create_project(
    project: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new project."""
    import uuid

    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id,
        "user_id": user_id,
        "name": project.name,
        "description": project.description,
        "paper_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

    _projects_db[project_id] = project_data

    return {
        "success": True,
        "data": project_data,
    }


@router.get("", response_model=dict)
async def list_projects(user_id: str = Depends(get_current_user_id)):
    """List all projects for the current user."""
    user_projects = [
        p for p in _projects_db.values() if p["user_id"] == user_id
    ]

    return {
        "success": True,
        "data": {
            "projects": user_projects,
            "total": len(user_projects),
        },
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a project by ID."""
    project = _projects_db.get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "data": project,
    }


@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a project."""
    project = _projects_db.get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    del _projects_db[project_id]

    return {
        "success": True,
        "message": "Project deleted",
    }


@router.get("/{project_id}/papers", response_model=dict)
async def list_papers(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """List papers in a project."""
    project = _projects_db.get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Return empty list for now (replace with database query)
    return {
        "success": True,
        "data": {
            "papers": [],
            "total": 0,
        },
    }


@router.post("/{project_id}/papers", response_model=dict)
async def add_paper(
    project_id: str,
    paper: dict,
    user_id: str = Depends(get_current_user_id),
):
    """Add a paper to a project."""
    project = _projects_db.get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    import uuid

    paper_id = str(uuid.uuid4())
    paper_data = {
        "id": paper_id,
        "project_id": project_id,
        **paper,
        "created_at": "2024-01-01T00:00:00Z",
    }

    project["paper_count"] = project.get("paper_count", 0) + 1

    return {
        "success": True,
        "data": paper_data,
    }
