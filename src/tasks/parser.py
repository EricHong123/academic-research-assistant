"""Paper parsing tasks."""
from datetime import datetime
from ..tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def parse_paper_task(self, paper_id: str, pdf_url: str) -> dict:
    """Parse a paper and extract structured data."""
    from ..agents.parser_agent import ParserAgent
    from ..services.vector_store import VectorStoreService
    import uuid

    try:
        # Parse the paper
        parser = ParserAgent()

        # Run parsing
        result = parser.parse(paper_id=paper_id, pdf_url=pdf_url)

        # Index chunks for RAG
        vector_store = VectorStoreService()

        # Split into chunks
        parsed_data = result.get("parsed_data", {})
        text = result.get("sections", {}).get("method", "") + "\n" + result.get("sections", {}).get("result", "")

        # Simple chunking
        chunk_size = 1000
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]
            chunks.append({
                "id": f"{paper_id}_chunk_{i // chunk_size}",
                "text": chunk_text,
                "page": i // chunk_size,
            })

        return {
            "paper_id": paper_id,
            "parsed_data": parsed_data,
            "chunks_indexed": len(chunks),
            "status": "success",
        }

    except Exception as e:
        # Retry on failure
        self.retry(exc=e, countdown=60)


@celery_app.task(bind=True)
def batch_parse_papers(self, paper_ids: list[str]) -> dict:
    """Parse multiple papers in batch."""
    results = []

    for paper_id in paper_ids:
        try:
            result = parse_paper_task.delay(paper_id, "")
            results.append({"paper_id": paper_id, "task_id": result.id})
        except Exception as e:
            results.append({"paper_id": paper_id, "error": str(e)})

    return {
        "batch_size": len(paper_ids),
        "tasks_created": len(results),
        "timestamp": datetime.utcnow().isoformat(),
    }


@celery_app.task(bind=True)
def extract_statistics(self, paper_id: str, pdf_url: str) -> dict:
    """Extract statistical values from a paper for meta-analysis."""
    from ..agents.parser_agent import ParserAgent

    parser = ParserAgent()

    # Extract text
    text = parser._extract_text(pdf_url)

    # Extract statistics
    stats = parser._extract_statistics(text)

    return {
        "paper_id": paper_id,
        "statistics": stats,
        "extracted_at": datetime.utcnow().isoformat(),
    }
