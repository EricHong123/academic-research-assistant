"""PubMed database adapter using E-utilities API."""
import os
import httpx
from typing import Optional


class PubMedAdapter:
    """Adapter for PubMed/NCBI E-utilities API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self):
        self.api_key = os.getenv("PUBMED_API_KEY")

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search PubMed."""
        import urllib.parse

        # Build ESearch query
        terms = query.get("terms", [])
        phrases = query.get("phrases", [])
        operators = query.get("operators", [])

        # Build query string
        query_parts = []
        for term in terms:
            query_parts.append(term)
        for phrase in phrases:
            query_parts.append(f'"{phrase}"')

        query_str = " AND ".join(query_parts) if query_parts else query.get("original", "")

        # Apply filters
        if filters:
            if year_from := filters.get("year_from"):
                query_str += f" AND {year_from}[PDAT]"
            if year_to := filters.get("year_to"):
                query_str += f" : {year_to}[PDAT]"

        # ESearch
        async with httpx.AsyncClient() as client:
            # Search
            search_url = f"{self.BASE_URL}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query_str,
                "retmax": limit,
                "retmode": "json",
                "sort": "relevance",
            }
            if self.api_key:
                params["api_key"] = self.api_key

            search_resp = await client.get(search_url, params=params)
            search_data = search_resp.json()

            ids = search_data.get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            # ESummary for details
            summary_url = f"{self.BASE_URL}/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json",
            }
            if self.api_key:
                summary_params["api_key"] = self.api_key

            summary_resp = await client.get(summary_url, params=summary_params)
            summary_data = summary_resp.json()

            # Parse results
            papers = []
            for pubmed_id in ids:
                result = summary_data.get("result", {}).get(pubmed_id, {})
                if result.get("error"):
                    continue

                paper = self._parse_pubmed_result(pubmed_id, result)
                papers.append(paper)

            return papers

    def _parse_pubmed_result(self, pubmed_id: str, data: dict) -> dict:
        """Parse PubMed result to standard format."""
        authors = []
        for author in data.get("authors", []):
            name = author.get("name", "")
            if name:
                authors.append(name)

        # Get journal info
        source = data.get("source", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        pages = data.get("pages", "")

        journal_info = f"{source}"
        if volume:
            journal_info += f" {volume}"
        if issue:
            journal_info += f"({issue})"
        if pages:
            journal_info += f":{pages}"

        return {
            "id": pubmed_id,
            "title": data.get("title", ""),
            "authors": authors,
            "abstract": data.get("pubdate", ""),
            "year": self._extract_year(data.get("pubdate", "")),
            "source": "pubmed",
            "pmid": pubmed_id,
            "doi": data.get("elocationid", "").replace("doi: ", ""),
            "journal": source,
            "metadata": {
                "journal": journal_info,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "pubmed_id": pubmed_id,
            },
        }

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        import re

        match = re.search(r"(\d{4})", date_str)
        if match:
            return int(match.group(1))
        return None

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata for a PubMed paper."""
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": paper_id,
                "retmode": "xml",
            }
            if self.api_key:
                params["api_key"] = self.api_key

            response = await client.get(url, params=params)
            # Parse XML response
            # In production, use xml.etree.ElementTree
            return {"paper_id": paper_id, "format": "xml", "raw": response.text}

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF is not directly available from PubMed."""
        raise NotImplementedError("PubMed does not provide direct PDF downloads")
