"""Integration and unit tests for the VLM Rich Frame Ingestion and Extraction Service.
"""

import io
import json
import pytest
import cv2
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings, PROJECT_ROOT


@pytest.fixture(name="client")
def client_fixture():
    """Yields a test client with lifespan context active, overriding settings for testing."""
    old_sampling = settings.ENABLE_ADAPTIVE_SAMPLING
    settings.ENABLE_ADAPTIVE_SAMPLING = False
    try:
        with TestClient(app) as client:
            yield client
    finally:
        settings.ENABLE_ADAPTIVE_SAMPLING = old_sampling


def create_mock_video(file_path: Path, duration_sec: int = 3, fps: int = 10) -> None:
    """Helper to generate a real, readable video file using OpenCV."""
    width, height = 320, 240
    # Use MP4V codec for cross-platform support in headless environments
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(file_path), fourcc, float(fps), (width, height))

    if not out.isOpened():
        raise RuntimeError(f"Could not open VideoWriter for path: {file_path}")

    total_frames = duration_sec * fps
    for i in range(total_frames):
        # Create a black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Write timestamp text to frame
        sec = i / fps
        cv2.putText(
            frame,
            f"Time: {sec:.1f}s",
            (40, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        out.write(frame)

    out.release()


def test_frame_extraction_success(client: TestClient) -> None:
    """Verify rich frame extraction and VLM analysis returns statistics and validated metadata."""
    # 1. Create a real video of 3 seconds duration
    video_id = "00000000-0000-0000-0000-000000000001"
    video_filename = f"{video_id}.mp4"
    video_path = settings.VIDEOS_DIR / video_filename

    create_mock_video(video_path, duration_sec=3, fps=10)

    # 2. Write custom video metadata so VideoService thinks it exists
    video_metadata = {
        "video_id": video_id,
        "filename": "mock_3s_video.mp4",
        "upload_time": "2026-06-02T18:00:00Z",
        "file_size": video_path.stat().st_size,
    }
    metadata_path = settings.METADATA_DIR / f"{video_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as meta_file:
        json.dump(video_metadata, meta_file)

    # Ensure settings is set to Mock VLM Mode for tests
    assert settings.MOCK_MODEL is True

    # 3. Call endpoint to extract frames and run rich VLM analysis
    payload = {"video_id": video_id}
    response = client.post("/frames/extract", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == video_id
    assert data["processed_frames"] == 3
    assert data["successful_frames"] == 3
    assert data["failed_frames"] == 0

    frames = data["frames"]
    assert len(frames) == 3

    for idx, frame in enumerate(frames):
        assert frame["video_id"] == video_id
        assert frame["timestamp_seconds"] == float(idx)
        assert "frame_id" in frame
        assert "timestamp_human" in frame
        assert "scene_type" in frame
        assert "scene_description" in frame
        assert "caption" in frame
        assert "search_text" in frame
        assert "people_count" in frame
        assert isinstance(frame["objects"], list)
        assert isinstance(frame["activities"], list)
        assert isinstance(frame["keywords"], list)

        # Verify frame path string format (should be relative and forward-slash normalized)
        assert "data/frames/" in frame["frame_path"]

        # Verify frame exists on local storage
        absolute_frame_path = PROJECT_ROOT / frame["frame_path"]
        assert absolute_frame_path.exists()

        # Verify individual JSON metadata file exists under data/metadata/{video_id}/{frame_id}.json
        individual_json = settings.METADATA_DIR / video_id / f"{frame['frame_id']}.json"
        assert individual_json.exists()
        with open(individual_json, "r", encoding="utf-8") as ind_file:
            ind_data = json.load(ind_file)
            assert ind_data["frame_id"] == frame["frame_id"]
            assert ind_data["caption"] == frame["caption"]

    # Verify frame metadata catalog json file is saved in metadata root
    catalog_path = settings.METADATA_DIR / f"{video_id}_frames.json"
    assert catalog_path.exists()

    # 4. Check listing endpoint for video frames
    list_response = client.get(f"/frames/video/{video_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 3
    assert list_data[0]["frame_id"] == frames[0]["frame_id"]
    assert "scene_type" in list_data[0]


def test_frame_extraction_missing_video(client: TestClient) -> None:
    """Verify that requesting extraction on a missing video ID returns 404."""
    missing_id = "00000000-0000-0000-0000-999999999999"
    payload = {"video_id": missing_id}

    # Act
    response = client.post("/frames/extract", json=payload)

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_frame_extraction_malformed_id(client: TestClient) -> None:
    """Verify that requesting extraction on a malformed ID returns 400."""
    malformed_id = "not-a-valid-uuid"
    payload = {"video_id": malformed_id}

    # Act
    response = client.post("/frames/extract", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Invalid video ID format" in response.json()["detail"]


def test_get_frames_metadata_not_extracted_yet(client: TestClient) -> None:
    """Verify that getting frames metadata for a video with no frames extracted returns 404."""
    # 1. Register a video ID
    video_id = "00000000-0000-0000-0000-000000000002"
    video_filename = f"{video_id}.mp4"
    video_path = settings.VIDEOS_DIR / video_filename

    # Create dummy empty file so VideoService check passes
    video_path.write_bytes(b"empty")

    video_metadata = {
        "video_id": video_id,
        "filename": "unextracted.mp4",
        "upload_time": "2026-06-02T18:00:00Z",
        "file_size": 5,
    }
    metadata_path = settings.METADATA_DIR / f"{video_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as meta_file:
        json.dump(video_metadata, meta_file)

    # Act (attempt to get frames metadata before extracting)
    response = client.get(f"/frames/video/{video_id}")

    # Assert
    assert response.status_code == 404
    assert "not been extracted yet" in response.json()["detail"]
