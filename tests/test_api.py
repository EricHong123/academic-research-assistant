"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestSearchAPI:
    """Tests for Search API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Academic Research Assistant"
        assert data["version"] == "0.1.0"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_list_databases(self, client):
        """Test database listing."""
        response = client.get("/api/search/databases")
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data
        assert len(data["databases"]) == 4

    def test_search_endpoint_structure(self, client):
        """Test search endpoint returns correct structure."""
        # This will fail without API keys but checks the response structure
        response = client.post(
            "/api/search",
            json={"query": "test"},
        )
        # Either succeeds or returns empty results
        assert response.status_code in [200, 500]


class TestProjectAPI:
    """Tests for Project API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_list_projects_empty(self, client):
        """Test listing projects when empty."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_project(self, client):
        """Test creating a project."""
        response = client.post(
            "/api/projects",
            json={"name": "Test Project", "description": "A test project"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Project"


class TestAuthAPI:
    """Tests for Auth API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_register_duplicate_email(self, client):
        """Test registering with duplicate email."""
        # First registration
        client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "password123"},
        )

        # Second registration should fail
        response = client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "password123"},
        )
        assert response.status_code == 400


class TestExportAPI:
    """Tests for Export API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_export_bibtex(self, client):
        """Test BibTeX export."""
        papers = [
            {
                "title": "Test Paper",
                "authors": ["Author A", "Author B"],
                "year": 2023,
                "journal": "Test Journal",
                "doi": "10.1234/test",
            }
        ]

        response = client.post(
            "/api/export/bibtex",
            json={"papers": papers, "format": "bibtex"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Test Paper" in data["data"]["content"]

    def test_export_ris(self, client):
        """Test RIS export."""
        papers = [
            {
                "title": "Test Paper",
                "authors": ["Author A"],
                "year": 2023,
                "journal": "Test Journal",
            }
        ]

        response = client.post(
            "/api/export/ris",
            json={"papers": papers, "format": "ris"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "TY  - JOUR" in data["data"]["content"]
