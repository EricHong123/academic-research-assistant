"""Tests for utility modules."""
import pytest
from src.utils.text import (
    clean_text,
    truncate_text,
    extract_doi,
    normalize_authors,
    format_author_list,
    parse_year,
    count_words,
)
from src.utils.citation import format_citation_apa, format_citation_mla


class TestTextUtils:
    """Tests for text utilities."""

    def test_clean_text(self):
        """Test text cleaning."""
        text = "  Hello   World  \n\n  "
        assert clean_text(text) == "Hello World"

    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that should be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

    def test_extract_doi(self):
        """Test DOI extraction."""
        text = "The DOI is 10.1234/test.article"
        assert extract_doi(text) == "10.1234/test.article"

        text = "https://doi.org/10.1234/test"
        assert "10.1234/test" in extract_doi(text)

    def test_normalize_authors(self):
        """Test author normalization."""
        authors = ["JOHN SMITH", "jane doe"]
        normalized = normalize_authors(authors)
        assert "John Smith" in normalized
        assert "Jane Doe" in normalized

    def test_format_author_list(self):
        """Test author list formatting."""
        authors = ["Author A", "Author B", "Author C"]
        assert format_author_list(authors) == "Author A, Author B, & Author C"
        assert format_author_list([authors[0]]) == authors[0]
        assert "et al" in format_author_list(["A", "B", "C", "D", "E", "F", "G", "H"])

    def test_parse_year(self):
        """Test year parsing."""
        assert parse_year("2023") == 2023
        assert parse_year("2023-01-15") == 2023
        assert parse_year("Jan 2023") == 2023

    def test_count_words(self):
        """Test word counting."""
        assert count_words("Hello world") == 2
        assert count_words("One two three four five") == 5


class TestCitationUtils:
    """Tests for citation utilities."""

    def test_format_citation_apa(self):
        """Test APA citation formatting."""
        citation = format_citation_apa(
            authors=["Smith, J.", "Doe, J."],
            year=2023,
            title="Test Article",
            journal="Nature",
            volume="10",
            issue="2",
            pages="100-110",
            doi="10.1234/test",
        )

        # Check that key elements are present (format may vary)
        assert "2023" in citation
        assert "Test Article" in citation
        assert "Nature" in citation
        assert "10.1234/test" in citation

    def test_format_citation_mla(self):
        """Test MLA citation formatting."""
        citation = format_citation_mla(
            authors=["Smith, John"],
            year=2023,
            title="Test Article",
            journal="Science",
        )

        assert "Smith, John" in citation
        assert "2023" in citation
        assert "Science" in citation
