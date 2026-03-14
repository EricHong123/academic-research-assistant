"""Tests for paper models."""
import pytest
from src.models.paper import Paper, PaperMetadata, PaperSearchResult, ParsedPaperData


class TestPaper:
    """Tests for Paper model."""

    def test_paper_creation(self):
        """Test creating a paper."""
        paper = Paper(
            title="Test Paper",
            authors=["Author A", "Author B"],
            source="pubmed",
            year=2023,
        )

        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.source == "pubmed"
        assert paper.year == 2023

    def test_paper_with_metadata(self):
        """Test paper with metadata."""
        metadata = PaperMetadata(
            doi="10.1234/test",
            journal="Nature",
            quartile="Q1",
        )

        paper = Paper(
            title="Test Paper",
            authors=["Author A"],
            source="pubmed",
            metadata=metadata,
        )

        assert paper.metadata.doi == "10.1234/test"
        assert paper.metadata.quartile == "Q1"

    def test_paper_search_result(self):
        """Test paper search result with score."""
        paper = Paper(
            title="Test Paper",
            authors=["Author A"],
            source="pubmed",
        )

        result = PaperSearchResult(
            paper=paper,
            score=0.85,
        )

        assert result.score == 0.85
        assert result.paper.title == "Test Paper"


class TestParsedPaperData:
    """Tests for parsed paper data."""

    def test_parsed_data_creation(self):
        """Test creating parsed paper data."""
        parsed = ParsedPaperData(
            research_type="横断面",
            independent_vars=["工作满意度"],
            dependent_vars=["职业倦怠"],
            sample_size=500,
        )

        assert parsed.research_type == "横断面"
        assert "工作满意度" in parsed.independent_vars
        assert parsed.sample_size == 500

    def test_parsed_data_defaults(self):
        """Test parsed data default values."""
        parsed = ParsedPaperData()

        assert parsed.independent_vars == []
        assert parsed.dependent_vars == []
        assert parsed.sample_size is None
