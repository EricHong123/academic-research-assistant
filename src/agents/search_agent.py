"""Search agent for multi-database academic literature search."""
from typing import Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..models.search import SearchQuery
from ..models.paper import PaperSearchResult


class SearchAgent:
    """Agent for searching across multiple academic databases."""

    def __init__(self):
        self.adapters = {}
        self._init_adapters()

    def _init_adapters(self):
        """Initialize database adapters."""
        from ..services.adapters.pubmed_adapter import PubMedAdapter
        from ..services.adapters.wos_adapter import WOSAdapter
        from ..services.adapters.scopus_adapter import ScopusAdapter
        from ..services.adapters.google_scholar_adapter import GoogleScholarAdapter

        # Register available adapters
        self.adapters["pubmed"] = PubMedAdapter()
        self.adapters["wos"] = WOSAdapter()
        self.adapters["scopus"] = ScopusAdapter()
        self.adapters["google_scholar"] = GoogleScholarAdapter()

    async def search(
        self,
        query: str,
        databases: list[str] | None = None,
        filters: dict | None = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search across multiple databases."""
        import asyncio

        # Default to all available databases
        if databases is None:
            databases = list(self.adapters.keys())

        # Parse query
        parsed_query = self._parse_query(query)

        # Execute searches in parallel
        tasks = []
        for db in databases:
            if db in self.adapters:
                adapter = self.adapters[db]
                task = self._search_with_adapter(adapter, parsed_query, filters, limit)
                tasks.append((db, task))

        results_by_db = {}
        for db, task in tasks:
            try:
                results = await task
                results_by_db[db] = results
            except Exception as e:
                results_by_db[db] = []
                print(f"Error searching {db}: {e}")

        # Aggregate results
        aggregated = self._aggregate_results(results_by_db)

        # Rank results
        ranked = await self._rank_results(aggregated, query, filters)

        return ranked[:limit]

    def _parse_query(self, query: str) -> dict:
        """Parse boolean query expressions."""
        import re

        # Find phrases first (quoted strings)
        phrases = re.findall(r'"([^"]+)"', query)

        # Remove phrases and clean up
        temp_query = re.sub(r'"[^"]+"', '', query)

        # Split by operators
        tokens = re.split(r'\s+(AND|OR|NOT)\s+', temp_query)

        terms = []
        operators = []

        for i, token in enumerate(tokens):
            token = token.strip()
            if not token:
                continue
            if token.upper() in ("AND", "OR", "NOT"):
                operators.append(token.upper())
            elif token:
                terms.append(token)

        return {
            "terms": terms,
            "phrases": phrases,
            "operators": operators,
            "original": query,
        }

    async def _search_with_adapter(self, adapter, parsed_query: dict, filters: dict | None, limit: int) -> list[dict]:
        """Search with a specific adapter."""
        try:
            return await adapter.search(parsed_query, filters, limit)
        except Exception as e:
            print(f"Adapter error: {e}")
            return []

    def _aggregate_results(self, results_by_db: dict[str, list[dict]]) -> list[dict]:
        """Aggregate and deduplicate results from multiple databases."""
        seen_dois = set()
        aggregated = []

        for db, results in results_by_db.items():
            for paper in results:
                doi = paper.get("doi", "")
                # Deduplicate by DOI
                if doi and doi in seen_dois:
                    continue
                if doi:
                    seen_dois.add(doi)

                # Add source
                paper["sources"] = [db]
                aggregated.append(paper)

        return aggregated

    async def _rank_results(self, papers: list[dict], query: str, filters: dict | None = None) -> list[dict]:
        """Rank results using semantic similarity and other factors."""
        from ..services.llm import LLMService

        if not papers:
            return []

        llm = LLMService()

        # Get embeddings for query
        query_embedding = await llm.get_embedding(query)

        # Score each paper
        scored_papers = []
        for paper in papers:
            score = await self._calculate_relevance_score(paper, query, query_embedding)
            paper["relevance_score"] = score
            scored_papers.append(paper)

        # Sort by score
        scored_papers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # Apply filters
        if filters:
            scored_papers = self._apply_filters(scored_papers, filters)

        return scored_papers

    async def _calculate_relevance_score(
        self, paper: dict, query: str, query_embedding: list[float]
    ) -> float:
        """Calculate relevance score for a paper."""
        from ..services.llm import LLMService
        import math

        llm = LLMService()

        # Semantic similarity (0-0.4)
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        paper_embedding = await llm.get_embedding(text)
        semantic_score = self._cosine_similarity(query_embedding, paper_embedding) * 0.4

        # Journal quality (0-0.3)
        quartile = paper.get("metadata", {}).get("quartile", "")
        journal_quality = {
            "Q1": 0.3,
            "Q2": 0.21,
            "Q3": 0.12,
            "Q4": 0.03,
        }.get(quartile, 0.1)

        # Study design (0-0.3)
        paper_type = paper.get("paper_type", "").lower()
        study_design = {
            "meta_analysis": 0.3,
            "systematic_review": 0.28,
            "longitudinal": 0.27,
            "experimental": 0.24,
            "cross_sectional": 0.15,
        }.get(paper_type, 0.1)

        return semantic_score + journal_quality + study_design

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _apply_filters(self, papers: list[dict], filters: dict) -> list[dict]:
        """Apply filters to papers."""
        filtered = papers

        # Year filter
        if year_from := filters.get("year_from"):
            filtered = [p for p in filtered if p.get("year", 0) >= year_from]
        if year_to := filters.get("year_to"):
            filtered = [p for p in filtered if p.get("year", 9999) <= year_to]

        # Journal tier filter
        if tiers := filters.get("journal_tiers"):
            filtered = [
                p for p in filtered
                if p.get("metadata", {}).get("quartile") in tiers
            ]

        return filtered
