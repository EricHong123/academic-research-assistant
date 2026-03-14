"""EBSCOhost database adapter."""
import os
import httpx
from typing import Optional


class EBSCOAdapter:
    """Adapter for EBSCOhost EDS API."""

    BASE_URL = "https://eds-api.ebscohost.com"

    def __init__(self):
        self.api_key = os.getenv("EBSCO_API_KEY")
        self.profile = os.getenv("EBSCO_PROFILE", "edsapi")

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search EBSCOhost."""
        if not self.api_key:
            return []

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        query_str = query.get("original", "")

        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/edsapi/rest/search"
            params = {
                "searchterm": query_str,
                "resultsperpage": limit,
                "pagenumber": 1,
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
                print(f"EBSCO search error: {e}")
                return []

    def _parse_results(self, data: dict) -> list[dict]:
        """Parse EBSCO API response."""
        papers = []

        search_result = data.get("SearchResult", {})
        records = search_result.get("RecordList", {}).get("Record", [])

        for record in records:
            # Get basic info
            record_id = record.get("RecordId", "")

            # Get header info
            header = record.get("Header", {})
            pub_type = header.get("PubType", [])

            # Get items
            items = record.get("Item", [])
            title = ""
            authors = []
            journal = ""
            year = None
            doi = ""

            for item in items:
                label = item.get("Label", "")
                data_val = item.get("Data", "")

                if label == "Title":
                    title = data_val
                elif label == "Author":
                    authors.append(data_val)
                elif label == "Publication Date":
                    try:
                        year = int(data_val[:4])
                    except (ValueError, IndexError):
                        pass
                elif label == "DOI":
                    doi = data_val

            # Get source info
            if isinstance(pub_type, list):
                journal = pub_type[0] if pub_type else ""
            elif isinstance(pub_type, str):
                journal = pub_type

            papers.append({
                "id": record_id,
                "title": title,
                "authors": authors,
                "year": year,
                "source": "ebsco",
                "doi": doi,
                "journal": journal,
                "metadata": {
                    "record_id": record_id,
                    "pub_type": pub_type,
                },
            })

        return papers

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata."""
        if not self.api_key:
            return {}

        headers = {"x-api-key": self.api_key}

        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/edsapi/rest/retrieve"
            params = {"id": paper_id}

            try:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF is not available via EBSCO API."""
        raise NotImplementedError("EBSCO does not provide direct PDF downloads")
