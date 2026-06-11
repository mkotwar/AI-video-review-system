"""Unit and integration tests for Semantic Event Search and Qdrant integration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService


def test_embedding_service_mock_dimensions():
    """Verify that EmbeddingService generates mock vectors with correct dimension (1024 for BGE-M3)."""
    assert settings.MOCK_MODEL is True
    
    text = "Find a red vehicle entering the main gate."
    vector = EmbeddingService.generate_embeddings(text)
    
    assert isinstance(vector, list)
    assert len(vector) == 1024
    assert all(isinstance(val, float) for val in vector)


def test_search_service_indexing_and_retrieval():
    """Verify that SearchService can index and retrieve events using the local in-memory Qdrant client."""
    video_id = "test-search-video-1"
    
    mock_events = [
        {
            "event_id": "evt_001",
            "event_type": "vehicle_entry",
            "summary": "A red motorcycle arrived at gate 1.",
            "timestamp_start_human": "00:01:10",
            "timestamp_end_human": "00:01:15",
            "duration_seconds": 5.0,
            "objects": [{"type": "vehicle", "subtype": "motorcycle", "color": "red"}],
            "activities": ["arriving"]
        },
        {
            "event_id": "evt_002",
            "event_type": "pedestrian_crossing",
            "summary": "A person wearing a blue jacket walked across the street.",
            "timestamp_start_human": "00:02:30",
            "timestamp_end_human": "00:02:40",
            "duration_seconds": 10.0,
            "objects": [{"type": "pedestrian", "subtype": "person", "color": "blue"}],
            "activities": ["walking"]
        }
    ]
    
    # Index events
    success = SearchService.index_events(video_id, mock_events)
    assert success is True
    
    # Query events
    results = SearchService.search_events(query="motorcycle at gate", limit=5)
    assert len(results) >= 1
    
    # Check that query finds results and includes score and payload properties
    found_event_ids = [res["event_id"] for res in results]
    assert "evt_001" in found_event_ids
    
    first_hit = next(res for res in results if res["event_id"] == "evt_001")
    assert first_hit["video_id"] == video_id
    assert first_hit["event_type"] == "vehicle_entry"
    assert first_hit["description"] == "A red motorcycle arrived at gate 1."
    assert first_hit["duration_seconds"] == 5.0
    assert first_hit["score"] > 0.0


def test_search_api_endpoint_and_filtering():
    """Verify that the POST /api/v1/search API endpoint works correctly and filters results by video_id."""
    video_id_1 = "test-video-uuid-1"
    video_id_2 = "test-video-uuid-2"
    
    events_video_1 = [
        {
            "event_id": "evt_001",
            "event_type": "restricted_area_activity",
            "summary": "Intrusion detected in the back warehouse.",
            "timestamp_start_human": "00:00:10",
            "timestamp_end_human": "00:00:15",
            "duration_seconds": 5.0
        }
    ]
    events_video_2 = [
        {
            "event_id": "evt_001",
            "event_type": "restricted_area_activity",
            "summary": "Intrusion detected in the server office room.",
            "timestamp_start_human": "00:00:20",
            "timestamp_end_human": "00:00:25",
            "duration_seconds": 5.0
        }
    ]
    
    # Index events for both videos
    assert SearchService.index_events(video_id_1, events_video_1) is True
    assert SearchService.index_events(video_id_2, events_video_2) is True
    
    with TestClient(app) as client:
        # 1. Query without filters (should find both)
        response = client.post(
            "/api/v1/search",
            json={"query": "warehouse intrusion", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "warehouse intrusion"
        assert len(data["results"]) >= 2
        
        # 2. Query with video filter (should return only video_id_1)
        response_filtered = client.post(
            "/api/v1/search",
            json={"query": "intrusion", "limit": 10, "video_ids": [video_id_1]}
        )
        assert response_filtered.status_code == 200
        data_filtered = response_filtered.json()
        assert len(data_filtered["results"]) == 1
        assert data_filtered["results"][0]["video_id"] == video_id_1
        assert "warehouse" in data_filtered["results"][0]["description"]
