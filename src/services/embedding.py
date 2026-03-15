"""Embedding service using SiliconFlow API."""
import os
import httpx
from typing import List, Optional
from ..config import get_settings


class EmbeddingService:
    """Service for text embeddings using SiliconFlow API."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()
        self.model = model or settings.embedding_model
        self.api_key = api_key or settings.siliconflow_api_key
        self.base_url = base_url or settings.siliconflow_base_url
        self.dimension = settings.embedding_dimension

        if not self.api_key:
            raise ValueError("SiliconFlow API key is required")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Uses BAAI/bge-m3 model - best for bilingual academic text.
        Free tier available via SiliconFlow.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                },
            )
            response.raise_for_status()
            data = response.json()

            return [item["embedding"] for item in data["data"]]

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        embeddings = await self.embed_texts([query])
        return embeddings[0]


class RerankService:
    """Service for reranking using SiliconFlow API."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()
        self.model = model or settings.rerank_model
        self.api_key = api_key or settings.siliconflow_api_key
        self.base_url = base_url or settings.siliconflow_base_url

        if not self.api_key:
            raise ValueError("SiliconFlow API key is required")

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
    ) -> List[dict]:
        """
        Rerank documents based on query relevance.

        Uses BAAI/bge-reranker-v2-m3 model.
        Significantly improves RAG quality over simple vector similarity.

        Args:
            query: Query text
            documents: List of document texts to rerank
            top_n: Number of top documents to return (default: all)

        Returns:
            List of reranked documents with scores
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "query": query,
                    "documents": documents,
                    "top_n": top_n or len(documents),
                },
            )
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "index": item["index"],
                    "document": documents[item["index"]],
                    "relevance_score": item["relevance_score"],
                }
                for item in data["results"]
            ]


# Singleton instances
_embedding_service = None
_rerank_service = None


def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_rerank_service() -> RerankService:
    """Get singleton rerank service."""
    global _rerank_service
    if _rerank_service is None:
        _rerank_service = RerankService()
    return _rerank_service
