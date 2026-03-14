"""Scopus database adapter."""
import os
import httpx
from typing import Optional


class ScopusAdapter:
    """Adapter for Scopus API."""

    BASE_URL = "https://api.elsevier.com/content/search"

    def __init__(self):
        self.api_key = os.getenv("SCOPUS_API_KEY")

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search Scopus."""
        if not self.api_key:
            return []

        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
        }

        query_str = query.get("original", "")

        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/scopus"
            params = {
                "query": query_str,
                "count": limit,
                "start": 0,
            }

            try:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                return self._parse_results(data)
            except Exception as e:
                print(f"Scopus search error: {e}")
                return []

    def _parse_results(self, data: dict) -> list[dict]:
        """Parse Scopus API response."""
        papers = []

        search_results = data.get("search-results", {})
        entries = search_results.get("entry", [])

        for entry in entries:
            # Get IDs
            scopus_id = entry.get("eid", "")
            doi = entry.get("prism:doi", "")

            # Authors
            author_list = entry.get("author", [])
            authors = []
            if isinstance(author_list, list):
                authors = [
                    f"{a.get('given-name', '')} {a.get('surname', '')}"
                    for a in author_list
                    if a.get("surname")
                ]
            elif isinstance(author_list, dict):
                authors = [
                    f"{author_list.get('given-name', '')} {author_list.get('surname', '')}"
                ]

            # Publication info
            journal = entry.get("prism:publicationName", "")
            year = entry.get("prism:coverDate", "")
            if year:
                year = year[:4]

            volume = entry.get("prism:volume", "")
            issue = entry.get("prism:issueIdentifier", "")
            pages = entry.get("prism:pageRange", "")

            # Citation count
            cited_by = entry.get("citedby-count", 0)

            papers.append({
                "id": scopus_id,
                "title": entry.get("dc:title", ""),
                "authors": authors,
                "year": int(year) if year and year.isdigit() else None,
                "source": "scopus",
                "doi": doi,
                "journal": journal,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "metadata": {
                    "scopus_id": scopus_id,
                    "cited_by": cited_by,
                },
            })

        return papers

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata."""
        if not self.api_key:
            return {}

        headers = {"X-ELS-APIKey": self.api_key}

        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/scopus/{paper_id}"
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF is not available via Scopus API."""
        raise NotImplementedError("Scopus does not provide direct PDF downloads")
