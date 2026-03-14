"""Web of Science database adapter."""
import os
import httpx
from typing import Optional


class WOSAdapter:
    """Adapter for Web of Science API."""

    BASE_URL = "https://api.clarivate.com/apis/wos"

    def __init__(self):
        self.api_key = os.getenv("WOS_API_KEY")

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search Web of Science."""
        if not self.api_key:
            return []

        # Build query
        query_str = query.get("original", "")

        headers = {
            "X-ApiKey": self.api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            # Search
            search_url = f"{self.BASE_URL}/publications/v5"
            params = {
                "q": query_str,
                "limit": limit,
            }

            if filters:
                if year_from := filters.get("year_from"):
                    params["year"] = f"{year_from}-"
                if year_to := filters.get("year_to"):
                    if "year" in params:
                        params["year"] = f"{params['year'].rstrip('-')}-{year_to}"

            try:
                response = await client.get(
                    search_url,
                    params=params,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                return self._parse_results(data)
            except Exception as e:
                print(f"WOS search error: {e}")
                return []

    def _parse_results(self, data: dict) -> list[dict]:
        """Parse WOS API response."""
        papers = []

        records = data.get("records", [])
        for record in records:
            # Extract basic info
            uid = record.get("uid", "")
            title = record.get("title", {}).get("title", "")
            authors = [
                author.get("name", {}).get("fullName", "")
                for author in record.get("authors", [])
            ]

            # Journal info
            journal = record.get("source", {}).get("name", "")
            year = record.get("source", {}).get("year")
            volume = record.get("source", {}).get("volume")
            issue = record.get("source", {}).get("issue")
            pages = record.get("source", {}).get("pages")

            # DOI
            doi = ""
            for id in record.get("ids", []):
                if id.get("type") == "doi":
                    doi = id.get("value", "")
                    break

            # Citation count
            citation_count = record.get("citationCount", 0)

            papers.append({
                "id": uid,
                "title": title,
                "authors": authors,
                "year": year,
                "source": "wos",
                "doi": doi,
                "journal": journal,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "metadata": {
                    "wos_uid": uid,
                    "citation_count": citation_count,
                },
            })

        return papers

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata."""
        if not self.api_key:
            return {}

        headers = {"X-ApiKey": self.api_key}

        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/publications/v5/{paper_id}"
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF is not available via WOS API."""
        raise NotImplementedError("WOS does not provide direct PDF downloads")
