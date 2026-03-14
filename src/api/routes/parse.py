"""Parse API routes for paper analysis."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional


router = APIRouter()


class ParseRequest(BaseModel):
    """Parse request model."""

    paper_id: Optional[str] = None
    pdf_url: Optional[str] = None
    project_id: Optional[str] = None
    async_mode: bool = True


class ParseResponse(BaseModel):
    """Parse response model."""

    task_id: Optional[str] = None
    status: str
    message: str


@router.post("", response_model=dict)
async def parse_paper(request: ParseRequest, background_tasks: BackgroundTasks):
    """Parse a paper and extract structured data."""
    if not request.pdf_url and not request.paper_id:
        raise HTTPException(
            status_code=400,
            detail="Either paper_id or pdf_url must be provided"
        )

    if request.async_mode:
        # Queue the task
        from src.tasks.parser import parse_paper_task

        task = parse_paper_task.delay(
            request.paper_id or "unknown",
            request.pdf_url or ""
        )

        return {
            "success": True,
            "data": {
                "task_id": task.id,
                "status": "queued",
                "message": "Paper parsing task has been queued",
            },
        }
    else:
        # Run synchronously
        from src.agents.parser_agent import ParserAgent

        try:
            parser = ParserAgent()
            result = await parser.parse(
                paper_id=request.paper_id,
                pdf_url=request.pdf_url,
                project_id=request.project_id,
            )

            return {
                "success": True,
                "data": {
                    "status": "completed",
                    "result": result,
                },
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=dict)
async def get_parse_status(task_id: str):
    """Get the status of a parsing task."""
    from src.tasks.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is waiting to be processed",
            },
        }
    elif task.state == "SUCCESS":
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "success",
                "result": task.result,
            },
        }
    elif task.state == "FAILURE":
        return {
            "success": False,
            "data": {
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info),
            },
        }
    else:
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": task.state.lower(),
            },
        }
