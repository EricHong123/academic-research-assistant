"""Vector store service for RAG - Weaviate as default."""
import os
from typing import Optional, List, Dict, Any
from ..config import get_settings


class VectorStoreService:
    """Service for vector storage and retrieval using Weaviate."""

    def __init__(self, provider: str = None):
        settings = get_settings()
        self.provider = provider or settings.vector_db_provider
        self._client = None

    def _get_client(self):
        """Get or create Weaviate client."""
        if self._client is not None:
            return self._client

        settings = get_settings()

        if self.provider == "weaviate":
            try:
                import weaviate
                from weaviate.auth import AuthApiKey

                auth = None
                if settings.weaviate_api_key:
                    auth = AuthApiKey(api_key=settings.weaviate_api_key)

                self._client = weaviate.Client(
                    url=settings.weaviate_url,
                    auth_client_secret=auth,
                )
            except ImportError:
                raise ImportError(
                    "Weaviate client not installed. Install with: pip install weaviate-client"
                )

        elif self.provider == "pinecone":
            try:
                import pinecone

                pinecone.init(
                    api_key=settings.pinecone_api_key,
                    environment=settings.pinecone_environment,
                )
                self._client = pinecone
            except ImportError:
                raise ImportError(
                    "Pinecone client not installed. Install with: pip install pinecone"
                )

        return self._client

    async def create_index(
        self,
        name: str,
        dimension: int = None,
        description: str = "ARA Paper Index",
    ):
        """Create a new index (Weaviate class)."""
        settings = get_settings()
        dimension = dimension or settings.embedding_dimension

        client = self._get_client()

        if self.provider == "weaviate":
            # Check if schema exists
            if client.schema.exists(name):
                return

            # Create class schema
            class_schema = {
                "class": name,
                "description": description,
                "vectorizer": "none",  # We handle embeddings ourselves
                "moduleConfig": {
                    "text2vec-transformers": {
                        "vectorizeClassName": False
                    }
                },
                "properties": [
                    {"name": "paper_id", "dataType": ["text"]},
                    {"name": "title", "dataType": ["text"]},
                    {"name": "authors", "dataType": ["text"]},
                    {"name": "year", "dataType": ["int"]},
                    {"name": "journal", "dataType": ["text"]},
                    {"name": "chunk_text", "dataType": ["text"]},
                    {"name": "chunk_index", "dataType": ["int"]},
                    {"name": "page", "dataType": ["int"]},
                    {"name": "section", "dataType": ["text"]},
                ],
            }

            client.schema.create_class(class_schema)

        elif self.provider == "pinecone":
            if name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=name,
                    dimension=dimension,
                    metric="cosine",
                )

    async def delete_index(self, name: str):
        """Delete an index."""
        client = self._get_client()

        if self.provider == "weaviate":
            if client.schema.exists(name):
                client.schema.delete_class(name)

        elif self.provider == "pinecone":
            if name in pinecone.list_indexes():
                pinecone.delete_index(name)

    async def add_documents(
        self,
        index_name: str,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        """
        Add documents with embeddings to the index.

        Args:
            index_name: Name of the index/class
            documents: List of document metadata
            embeddings: List of embedding vectors
        """
        client = self._get_client()

        if self.provider == "weaviate":
            with client.batch as batch:
                for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                    batch.add_data_object(
                        data_object=doc,
                        class_name=index_name,
                        vector=embedding,
                    )

        elif self.provider == "pinecone":
            index = pinecone.Index(index_name)
            vectors = [
                {
                    "id": f"doc_{i}",
                    "values": embedding,
                    "metadata": doc,
                }
                for i, (doc, embedding) in enumerate(zip(documents, embeddings))
            ]
            index.upsert(vectors=vectors)

    async def search(
        self,
        index_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar documents.

        Args:
            index_name: Name of the index/class
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters

        Returns:
            List of matching documents with scores
        """
        client = self._get_client()

        if self.provider == "weaviate":
            search = client.query.get(
                index_name,
                [
                    "paper_id",
                    "title",
                    "authors",
                    "year",
                    "journal",
                    "chunk_text",
                    "chunk_index",
                    "page",
                    "section",
                ],
            ).with_near_vector(
                {"vector": query_embedding}
            ).with_limit(top_k)

            if filters:
                where_filter = self._build_weaviate_filter(filters)
                search = search.with_where(where_filter)

            results = search.do()
            return [
                {
                    "id": item["id"],
                    "score": 1 - item.get("_distance", 0),  # Convert distance to similarity
                    "metadata": item.get("properties", {}),
                }
                for item in results["data"]["Get"][index_name]
            ]

        elif self.provider == "pinecone":
            index = pinecone.Index(index_name)
            result = index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filters,
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

    def _build_weaviate_filter(self, filters: Dict) -> Dict:
        """Convert simple filters to Weaviate format."""
        # Simplified filter conversion
        where = {"operator": "And", "operands": []}
        for key, value in filters.items():
            where["operands"].append({
                "path": [key],
                "operator": "Equal",
                "valueText": value
            })
        return where


# Singleton instance
_vector_store = None


def get_vector_store(provider: str = None) -> VectorStoreService:
    """Get singleton vector store service."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService(provider)
    return _vector_store
