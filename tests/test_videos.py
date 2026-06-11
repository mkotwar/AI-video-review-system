"""Integration and unit tests for the Video Upload Service and API router.
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.video import VideoService
from app.core.config import settings


@pytest.fixture(name="client")
def client_fixture():
    """Yields a test client with lifespan context active, ensuring directories exist."""
    with TestClient(app) as client:
        yield client


def test_upload_valid_formats(client: TestClient) -> None:
    """Verify that uploading valid video formats (mp4, avi, mov) succeeds."""
    formats = [
        ("test_video.mp4", "video/mp4"),
        ("test_video.avi", "video/x-msvideo"),
        ("test_video.mov", "video/quicktime"),
    ]

    for filename, mime_type in formats:
        # Create a mock video file (100 dummy bytes)
        file_bytes = b"MOCK_VIDEO_DATA_" * 10
        files = {"file": (filename, io.BytesIO(file_bytes), mime_type)}

        # Act
        response = client.post("/videos/upload", files=files)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "video_id" in data
        assert data["filename"] == filename
        assert data["file_size"] == len(file_bytes)
        assert "upload_time" in data

        # Verify filesystem storage
        video_id = data["video_id"]
        meta_file = settings.METADATA_DIR / f"{video_id}.json"
        video_file = settings.VIDEOS_DIR / f"{video_id}{Path(filename).suffix.lower()}"

        assert meta_file.exists()
        assert video_file.exists()
        assert video_file.read_bytes() == file_bytes


def test_upload_invalid_format(client: TestClient) -> None:
    """Verify that uploading invalid formats returns a 400 validation error."""
    invalid_files = [
        ("document.txt", b"simple text file content", "text/plain"),
        ("image.png", b"fake png signature bytes", "image/png"),
        ("archive.zip", b"fake zip contents", "application/zip"),
    ]

    for filename, file_bytes, mime_type in invalid_files:
        files = {"file": (filename, io.BytesIO(file_bytes), mime_type)}

        # Act
        response = client.post("/videos/upload", files=files)

        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Unsupported video format" in response.json()["detail"]


def test_upload_empty_file(client: TestClient) -> None:
    """Verify that uploading an empty video file fails with a 400 validation error."""
    files = {"file": ("empty.mp4", io.BytesIO(b""), "video/mp4")}

    # Act
    response = client.post("/videos/upload", files=files)

    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "empty" in response.json()["detail"]


def test_get_video_metadata(client: TestClient) -> None:
    """Verify metadata lookup for existing and non-existing video IDs."""
    # 1. Test existing lookup
    filename = "lookup_test.mp4"
    file_bytes = b"LOOKUP_MOCK_BYTES"
    files = {"file": (filename, io.BytesIO(file_bytes), "video/mp4")}
    upload_resp = client.post("/videos/upload", files=files)
    video_id = upload_resp.json()["video_id"]

    # Act
    response = client.get(f"/videos/{video_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == video_id
    assert data["filename"] == filename
    assert data["file_size"] == len(file_bytes)

    # 2. Test non-existing ID lookup (valid UUID format)
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response_missing = client.get(f"/videos/{non_existent_id}")
    assert response_missing.status_code == 404
    assert "not found" in response_missing.json()["detail"].lower()

    # 3. Test malformed ID lookup (non-UUID format)
    malformed_id = "invalid-video-id-123"
    response_malformed = client.get(f"/videos/{malformed_id}")
    assert response_malformed.status_code == 400
    assert "Invalid video ID format" in response_malformed.json()["detail"]


def test_download_or_stream_video(client: TestClient) -> None:
    """Verify file download streaming endpoints and Content-Type matching."""
    formats = [
        ("stream_test.mp4", b"mp4_dummy_payload", "video/mp4"),
        ("stream_test.avi", b"avi_dummy_payload", "video/x-msvideo"),
        ("stream_test.mov", b"mov_dummy_payload", "video/quicktime"),
    ]

    for filename, file_bytes, expected_mime in formats:
        files = {"file": (filename, io.BytesIO(file_bytes), expected_mime)}
        upload_resp = client.post("/videos/upload", files=files)
        video_id = upload_resp.json()["video_id"]

        # Act
        response = client.get(f"/videos/{video_id}/download")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == expected_mime
        assert response.content == file_bytes


def test_list_videos(client: TestClient) -> None:
    """Verify retrieval list contains all processed metadata definitions."""
    # Register multiple mock videos
    videos = ["v1.mp4", "v2.avi", "v3.mov"]
    for idx, filename in enumerate(videos):
        files = {"file": (filename, io.BytesIO(f"list_data_{idx}".encode()), "video/mp4")}
        client.post("/videos/upload", files=files)

    # Act
    response = client.get("/videos/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check structure schema of elements
    for item in data:
        assert "video_id" in item
        assert "filename" in item
        assert "file_size" in item
        assert "upload_time" in item
