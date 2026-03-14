"""Database adapters for academic search."""
from .base import DatabaseAdapter
from .pubmed_adapter import PubMedAdapter
from .wos_adapter import WOSAdapter
from .scopus_adapter import ScopusAdapter
from .google_scholar_adapter import GoogleScholarAdapter

__all__ = [
    "DatabaseAdapter",
    "PubMedAdapter",
    "WOSAdapter",
    "ScopusAdapter",
    "GoogleScholarAdapter",
]
