"""Unit tests for the FastAPI application main and health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """Fixture to yield a test client with lifespan events executed."""
    with TestClient(app) as client:
        yield client


def test_health_check(client: TestClient) -> None:
    """Verify that the health check endpoint returns 200 and the expected keys."""
    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app_name" in data
    assert "environment" in data
    assert "debug_mode" in data
    assert "storage_checks" in data
    assert "timestamp" in data

    # Detailed content assert
    assert data["app_name"] == "AI Video Search Engine"
    assert data["status"] == "healthy"  # Storage directories must be auto-created during lifespan startup
    assert isinstance(data["storage_checks"], dict)
    assert data["storage_checks"]["data_directory"] == "accessible"
    assert data["storage_checks"]["videos_directory"] == "accessible"
    assert data["storage_checks"]["frames_directory"] == "accessible"
    assert data["storage_checks"]["metadata_directory"] == "accessible"
    assert data["storage_checks"]["logs_directory"] == "accessible"
