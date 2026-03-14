"""Base adapter interface for academic databases."""
from abc import ABC, abstractmethod
from typing import Protocol, Optional


class DatabaseAdapter(Protocol):
    """Protocol for database adapters."""

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search the database."""
        ...

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata for a paper."""
        ...

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF for a paper."""
        ...
