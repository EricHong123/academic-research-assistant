"""Search API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...models.search import SearchQuery, SearchResponse
from ...agents.search_agent import SearchAgent


router = APIRouter()


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    databases: list[str] | None = None
    filters: dict | None = None
    limit: int = 50
    project_id: str | None = None


class SearchResultResponse(BaseModel):
    """Response wrapper."""

    success: bool = True
    data: dict
    error: str | None = None


@router.post("", response_model=SearchResultResponse)
async def search_papers(request: SearchRequest):
    """Search academic papers across multiple databases."""
    try:
        agent = SearchAgent()

        results = await agent.search(
            query=request.query,
            databases=request.databases,
            filters=request.filters,
            project_id=request.project_id,
            limit=request.limit,
        )

        return SearchResultResponse(
            success=True,
            data={
                "papers": results,
                "total": len(results),
                "query": request.query,
                "databases": request.databases or ["pubmed"],
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/databases")
async def list_databases():
    """List available databases."""
    return {
        "databases": [
            {"id": "pubmed", "name": "PubMed", "type": "biomedical"},
            {"id": "wos", "name": "Web of Science", "type": "multidisciplinary"},
            {"id": "scopus", "name": "Scopus", "type": "multidisciplinary"},
            {"id": "google_scholar", "name": "Google Scholar", "type": "multidisciplinary"},
        ]
    }
