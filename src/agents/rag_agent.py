"""RAG agent for conversational interface with papers."""
from typing import Optional
from ..models.chat import ChatMessage, Citation


class RAGAgent:
    """Agent for RAG-based conversations about papers."""

    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200

    async def chat(
        self,
        project_id: str,
        message: str,
        history: list[dict] | None = None,
    ) -> dict:
        """Chat with papers in a project."""
        from ..services.llm import LLMService
        from ..services.vector_store import VectorStore

        llm = LLMService()
        vector_store = VectorStore()

        # Retrieve relevant context
        context = await vector_store.retrieve(
            project_id=project_id,
            query=message,
            top_k=5,
        )

        # Build conversation context
        conversation_context = self._build_context(history or [], context)

        # Generate answer with citations
        answer = await self._generate_answer(
            query=message,
            context=conversation_context,
            llm=llm,
        )

        # Extract citations from context
        citations = self._extract_citations(context)

        return {
            "answer": answer,
            "citations": [c.model_dump() for c in citations],
            "referenced_papers": self._get_referenced_papers(context),
        }

    async def _generate_answer(
        self,
        query: str,
        context: list[dict],
        llm,
    ) -> str:
        """Generate answer with strict citation requirements."""
        # Build context string with citations
        context_parts = []
        for i, chunk in enumerate(context):
            context_parts.append(
                f"[{i + 1}] {chunk.get('title', 'Unknown')}, {chunk.get('authors', 'Unknown authors')}, {chunk.get('year', 'Unknown year')}:\n"
                f"{chunk.get('text', '')}\n"
            )

        context_str = "\n".join(context_parts)

        prompt = f"""You are an academic research assistant. Answer the user's question based ONLY on the provided context.

IMPORTANT RULES:
1. Every sentence MUST cite sources using the format [number]
2. If you cannot find information in the context, say "I couldn't find information about this in the provided papers."
3. Do not make up information or cite sources not in the context
4. Be precise and academic in your response

Context from papers:
{context_str}

User question: {query}

Provide a well-cited academic answer:"""

        answer = await llm.generate(prompt, max_tokens=2000)

        return answer

    def _build_context(self, history: list[dict], retrieved_chunks: list[dict]) -> str:
        """Build context string from history and retrieved chunks."""
        context_parts = []

        # Add recent history
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context_parts.append(f"{role.upper()}: {content}")

        # Add retrieved chunks
        for chunk in retrieved_chunks:
            text = chunk.get("text", "")
            title = chunk.get("title", "")
            context_parts.append(f"PAPER: {title}\n{text}")

        return "\n\n".join(context_parts)

    def _extract_citations(self, context: list[dict]) -> list[Citation]:
        """Extract citations from retrieved context."""
        citations = []

        for chunk in context:
            citation = Citation(
                paper_id=chunk.get("paper_id", ""),
                authors=chunk.get("authors", ""),
                year=chunk.get("year", 0),
                page=chunk.get("page"),
                text=chunk.get("text", "")[:200],
            )
            citations.append(citation)

        return citations

    def _get_referenced_papers(self, context: list[dict]) -> list[dict]:
        """Get unique referenced papers."""
        seen = set()
        papers = []

        for chunk in context:
            paper_id = chunk.get("paper_id")
            if paper_id and paper_id not in seen:
                seen.add(paper_id)
                papers.append({
                    "id": paper_id,
                    "title": chunk.get("title"),
                    "authors": chunk.get("authors"),
                    "year": chunk.get("year"),
                })

        return papers


class VectorStore:
    """Vector store for RAG."""

    async def retrieve(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Retrieve relevant chunks for a query."""
        from ..services.llm import LLMService

        # This would connect to Pinecone/Weaviate in production
        # For now, return mock data
        llm = LLMService()

        # Get query embedding
        query_embedding = await llm.get_embedding(query)

        # In production, this would query the vector database
        # with the embedding and filter by project_id
        return [
            {
                "paper_id": "sample-1",
                "title": "Sample Paper Title",
                "authors": "Author A, Author B",
                "year": 2023,
                "text": "This is sample context that would be retrieved...",
                "score": 0.95,
            }
        ]

    async def index_paper(
        self,
        project_id: str,
        paper_id: str,
        chunks: list[dict],
    ) -> None:
        """Index paper chunks into vector store."""
        # In production, this would index chunks to Pinecone/Weaviate
        pass
