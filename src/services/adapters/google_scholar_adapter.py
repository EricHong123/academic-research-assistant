"""Google Scholar adapter using scholarly library."""
import os
from typing import Optional


class GoogleScholarAdapter:
    """Adapter for Google Scholar using scholarly Python library."""

    def __init__(self):
        self.enabled = os.getenv("GOOGLE_SCHOLAR_ENABLED", "false").lower() == "true"

    async def search(
        self,
        query: dict,
        filters: Optional[dict] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search Google Scholar."""
        if not self.enabled:
            return []

        try:
            from scholarly import scholarly, ProxyGenerator

            # Setup proxy if needed
            # pg = ProxyGenerator()
            # pg.SingleProxy(http=socks_proxy, https=socks_proxy)
            # scholarly.use_proxy(pg)

            search_query = query.get("original", "")

            # Search
            search_results = scholarly.search_pubs(search_query)

            papers = []
            count = 0

            for result in search_results:
                if count >= limit:
                    break

                paper = self._parse_result(result)
                if paper:
                    papers.append(paper)
                    count += 1

            return papers

        except ImportError:
            print("scholarly library not installed")
            return []
        except Exception as e:
            print(f"Google Scholar search error: {e}")
            return []

    def _parse_result(self, result: dict) -> dict:
        """Parse Google Scholar result."""
        # Extract bib info
        bib = result.get("bib", {})

        # Authors
        authors = bib.get("author", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(" and ")]

        # Year
        year = bib.get("pub_year")
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None

        # Extract citation count
        num_citations = result.get("num_citations", 0)

        # DOI
        doi = bib.get("doi", "")

        # Title
        title = bib.get("title", "")

        return {
            "id": result.get("eid", ""),
            "title": title,
            "authors": authors,
            "year": year,
            "source": "google_scholar",
            "doi": doi,
            "journal": bib.get("venue", ""),
            "abstract": bib.get("abstract", ""),
            "url": result.get("pub_url", ""),
            "metadata": {
                "citations": num_citations,
                "gsid": result.get("gsid", ""),
            },
        }

    async def get_metadata(self, paper_id: str) -> dict:
        """Get detailed metadata."""
        # Not supported for Google Scholar
        return {}

    async def download_pdf(self, paper_id: str) -> bytes:
        """Download PDF is not available via Google Scholar."""
        raise NotImplementedError("Google Scholar does not provide direct PDF downloads")
