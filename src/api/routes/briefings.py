"""Briefings API routes for trend reports."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel


router = APIRouter()


# In-memory storage
_briefings: dict[str, dict] = {}
_trackers: dict[str, dict] = {}


class TrackerCreate(BaseModel):
    """Create tracker request."""

    query: str
    frequency: str = "weekly"
    project_id: Optional[str] = None


def get_current_user_id() -> str:
    """Get current user ID."""
    return "demo-user"


@router.get("", response_model=dict)
async def list_briefings(user_id: str = Depends(get_current_user_id)):
    """List all briefings."""
    user_briefings = [
        b for b in _briefings.values() if b.get("user_id") == user_id
    ]

    return {
        "success": True,
        "data": {
            "briefings": user_briefings,
            "total": len(user_briefings),
        },
    }


@router.get("/{briefing_id}", response_model=dict)
async def get_briefing(
    briefing_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a specific briefing."""
    briefing = _briefings.get(briefing_id)

    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    if briefing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "data": briefing,
    }


@router.post("/trackers", response_model=dict)
async def create_tracker(
    tracker: TrackerCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new tracker for automated briefings."""
    import uuid

    tracker_id = str(uuid.uuid4())
    tracker_data = {
        "id": tracker_id,
        "user_id": user_id,
        "query": tracker.query,
        "frequency": tracker.frequency,
        "project_id": tracker.project_id,
        "last_run": None,
        "created_at": "2024-01-01T00:00:00Z",
    }

    _trackers[tracker_id] = tracker_data

    return {
        "success": True,
        "data": tracker_data,
    }


@router.get("/trackers", response_model=dict)
async def list_trackers(user_id: str = Depends(get_current_user_id)):
    """List all trackers."""
    user_trackers = [
        t for t in _trackers.values() if t.get("user_id") == user_id
    ]

    return {
        "success": True,
        "data": {
            "trackers": user_trackers,
            "total": len(user_trackers),
        },
    }


@router.delete("/trackers/{tracker_id}", response_model=dict)
async def delete_tracker(
    tracker_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a tracker."""
    tracker = _trackers.get(tracker_id)

    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    if tracker.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    del _trackers[tracker_id]

    return {
        "success": True,
        "message": "Tracker deleted",
    }


@router.post("/trackers/{tracker_id}/run", response_model=dict)
async def run_tracker(
    tracker_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Manually run a tracker to generate a briefing."""
    tracker = _trackers.get(tracker_id)

    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    if tracker.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # TODO: Implement actual briefing generation
    briefing = {
        "id": str(uuid.uuid4()),
        "tracker_id": tracker_id,
        "query": tracker["query"],
        "summary": "This is a generated briefing summary.",
        "papers": [],
        "created_at": "2024-01-01T00:00:00Z",
    }

    import uuid

    _briefings[briefing["id"]] = briefing

    return {
        "success": True,
        "data": briefing,
    }
