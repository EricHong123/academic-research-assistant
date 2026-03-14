"""Vector store service for RAG."""
import os
from typing import Optional


class VectorStoreService:
    """Service for vector storage and retrieval."""

    def __init__(self, provider: str = "pinecone"):
        self.provider = provider
        self._client = None

    def _get_client(self):
        """Get vector store client."""
        if self._client is not None:
            return self._client

        if self.provider == "pinecone":
            import pinecone

            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT", "us-west1"),
            )
            self._client = pinecone
        elif self.provider == "weaviate":
            import weaviate

            self._client = weaviate.Client(
                url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            )

        return self._client

    async def create_index(self, name: str, dimension: int = 1536):
        """Create a new index."""
        client = self._get_client()

        if self.provider == "pinecone":
            if name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=name,
                    dimension=dimension,
                    metric="cosine",
                )

    async def delete_index(self, name: str):
        """Delete an index."""
        client = self._get_client()

        if self.provider == "pinecone":
            if name in pinecone.list_indexes():
                pinecone.delete_index(name)

    async def upsert(
        self,
        index_name: str,
        vectors: list[dict],
    ):
        """Upsert vectors into index."""
        client = self._get_client()

        if self.provider == "pinecone":
            index = pinecone.Index(index_name)
            index.upsert(vectors=vectors)

    async def query(
        self,
        index_name: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: Optional[dict] = None,
    ) -> list[dict]:
        """Query index for similar vectors."""
        client = self._get_client()

        if self.provider == "pinecone":
            index = pinecone.Index(index_name)
            result = index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
            )

            return [
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {}),
                }
                for match in result.get("matches", [])
            ]

        return []


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStoreService:
    """Get singleton vector store service."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
