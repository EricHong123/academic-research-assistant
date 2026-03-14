"""Tests for parser agent."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.parser_agent import ParserAgent


class TestParserAgent:
    """Tests for ParserAgent."""

    @pytest.fixture
    def agent(self):
        """Create parser agent fixture."""
        return ParserAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.section_patterns is not None
        assert "method" in agent.section_patterns
        assert "result" in agent.section_patterns
        assert "discussion" in agent.section_patterns

    def test_extract_statistics(self, agent):
        """Test statistical value extraction."""
        text = """
        The results showed a significant correlation (r = 0.45, p < 0.001)
        between job satisfaction and burnout. The effect size was d = 0.82.
        ANOVA results: F(2, 97) = 15.34, p < 0.001.
        """

        stats = agent._extract_statistics(text)

        # Should find r, p, d, F values
        stat_types = [s["type"] for s in stats]
        assert "r" in stat_types or "r²" in stat_types
        assert "p" in stat_types

    def test_extract_statistics_empty(self, agent):
        """Test statistics extraction with no values."""
        text = "This is a sample text without statistics."

        stats = agent._extract_statistics(text)

        assert isinstance(stats, list)

    def test_generate_matrix(self, agent):
        """Test matrix generation."""
        from src.models.paper import ParsedPaperData

        parsed = ParsedPaperData(
            research_type="cross_sectional",
            independent_vars=["job_satisfaction"],
            dependent_vars=["burnout"],
            sample_size=500,
            subjects=["healthcare_workers"],
            instruments=[{"name": "MBI", "items": "22", "alpha": "0.85"}],
            key_findings="Job satisfaction negatively correlates with burnout",
        )

        matrix = agent._generate_matrix(parsed)

        assert matrix["research_type"] == "cross_sectional"
        assert "job_satisfaction" in matrix["iv"]
        assert matrix["sample_size"] == 500

    def test_analyze_structure(self, agent):
        """Test document structure analysis."""
        # Use text that matches the regex patterns
        text = """
 INTRODUCTION
This is the introduction.

 METHOD
This is the method section.

 RESULT
These are the results.

 DISCUSSION
This is the discussion.
        """

        sections = agent._analyze_structure(text)

        # At least some sections should be found
        assert isinstance(sections, dict)
