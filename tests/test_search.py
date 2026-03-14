"""Tests for search functionality."""
import pytest
from src.models.search import SearchQuery, SearchFilters


class TestSearchQuery:
    """Tests for SearchQuery model."""

    def test_search_query_creation(self):
        """Test creating a search query."""
        query = SearchQuery(
            query="machine learning",
            databases=["pubmed", "wos"],
            limit=50,
        )

        assert query.query == "machine learning"
        assert "pubmed" in query.databases
        assert query.limit == 50

    def test_search_query_defaults(self):
        """Test default values."""
        query = SearchQuery(query="test")

        assert query.databases == ["pubmed"]
        assert query.limit == 50
        assert query.filters.year_from is None


class TestSearchFilters:
    """Tests for SearchFilters model."""

    def test_filters_creation(self):
        """Test creating search filters."""
        filters = SearchFilters(
            year_from=2020,
            year_to=2024,
            journal_tiers=["Q1", "Q2"],
        )

        assert filters.year_from == 2020
        assert filters.year_to == 2024
        assert "Q1" in filters.journal_tiers

    def test_filters_defaults(self):
        """Test default filter values."""
        filters = SearchFilters()

        assert filters.year_from is None
        assert filters.year_to is None
        assert filters.journal_tiers == []
