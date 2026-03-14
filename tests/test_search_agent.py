"""Tests for search agent."""
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.search_agent import SearchAgent


class TestSearchAgent:
    """Tests for SearchAgent."""

    @pytest.fixture
    def agent(self):
        """Create search agent fixture."""
        return SearchAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes with adapters."""
        assert "pubmed" in agent.adapters
        assert "wos" in agent.adapters
        assert "scopus" in agent.adapters
        assert "google_scholar" in agent.adapters

    def test_parse_query_boolean(self, agent):
        """Test boolean query parsing."""
        result = agent._parse_query("machine learning AND deep learning")

        # Terms will include multi-word phrases
        assert "machine learning" in result["terms"]
        assert "deep learning" in result["terms"]
        assert "AND" in result["operators"]

    def test_parse_query_phrase(self, agent):
        """Test phrase query parsing."""
        result = agent._parse_query('"deep learning" AND neural networks')

        assert "neural networks" in result["terms"]
        assert "deep learning" in result["phrases"]
        assert "AND" in result["operators"]

    def test_cosine_similarity(self, agent):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        sim_same = agent._cosine_similarity(vec1, vec2)
        sim_different = agent._cosine_similarity(vec1, vec3)

        assert sim_same == 1.0
        assert sim_different == 0.0

    def test_apply_filters_year(self, agent):
        """Test applying year filters."""
        papers = [
            {"year": 2020},
            {"year": 2022},
            {"year": 2024},
        ]

        filtered = agent._apply_filters(papers, {"year_from": 2021, "year_to": 2023})

        assert len(filtered) == 1
        assert filtered[0]["year"] == 2022

    def test_apply_filters_quartile(self, agent):
        """Test applying quartile filters."""
        papers = [
            {"metadata": {"quartile": "Q1"}},
            {"metadata": {"quartile": "Q2"}},
            {"metadata": {"quartile": "Q4"}},
        ]

        filtered = agent._apply_filters(papers, {"journal_tiers": ["Q1", "Q2"]})

        assert len(filtered) == 2
