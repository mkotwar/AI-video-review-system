"""Unit and integration tests for Adaptive Frame Sampling.
"""

import json
import pytest
import cv2
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings, PROJECT_ROOT
from app.services.frame import FrameExtractionService


@pytest.fixture(name="client")
def client_fixture():
    """Yields a test client with lifespan context active, forcing adaptive sampling on."""
    old_sampling = settings.ENABLE_ADAPTIVE_SAMPLING
    settings.ENABLE_ADAPTIVE_SAMPLING = True
    try:
        with TestClient(app) as client:
            yield client
    finally:
        settings.ENABLE_ADAPTIVE_SAMPLING = old_sampling


def create_dynamic_video(file_path: Path, duration_sec: int = 5, fps: int = 10) -> None:
    """Helper to generate a video file where some frames are identical and others change."""
    width, height = 320, 240
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(file_path), fourcc, float(fps), (width, height))

    if not out.isOpened():
        raise RuntimeError(f"Could not open VideoWriter for path: {file_path}")

    total_frames = duration_sec * fps
    for i in range(total_frames):
        # Create a frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Second 0 to 2 (first 20 frames): identical black frames
        # Second 2 to 5 (next 30 frames): white frames with changing text (significant scene change)
        if i >= 20:
            frame.fill(255)
            cv2.putText(
                frame,
                f"Change: {i}",
                (40, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2,
            )
        out.write(frame)

    out.release()


def test_compute_similarity_metrics():
    """Test individual metrics on identical and different frames."""
    # Create identical frames
    frame1 = np.zeros((240, 320, 3), dtype=np.uint8)
    frame2 = np.zeros((240, 320, 3), dtype=np.uint8)
    
    hist_diff, ssim_diff, motion_score = FrameExtractionService.compute_similarity_metrics(frame1, frame2)
    assert hist_diff == 0.0
    assert ssim_diff == 0.0
    assert motion_score == 0.0

    # Create completely different frames (black and white)
    frame3 = np.ones((240, 320, 3), dtype=np.uint8) * 255
    hist_diff2, ssim_diff2, motion_score2 = FrameExtractionService.compute_similarity_metrics(frame1, frame3)
    assert hist_diff2 > 0.5
    assert ssim_diff2 > 0.5
    assert motion_score2 > 0.5


def test_adaptive_sampling_integration(client: TestClient) -> None:
    """Verify that adaptive sampling reduces the frames sent to Qwen VLM and populates metrics."""
    video_id = "00000000-0000-0000-0000-000000000005"
    video_filename = f"{video_id}.mp4"
    video_path = settings.VIDEOS_DIR / video_filename

    create_dynamic_video(video_path, duration_sec=5, fps=10)

    # Write custom video metadata
    video_metadata = {
        "video_id": video_id,
        "filename": "adaptive_test.mp4",
        "upload_time": "2026-06-03T18:00:00Z",
        "file_size": video_path.stat().st_size,
    }
    metadata_path = settings.METADATA_DIR / f"{video_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as meta_file:
        json.dump(video_metadata, meta_file)

    # Call endpoint with adaptive sampling enabled (via client_fixture)
    payload = {"video_id": video_id}
    response = client.post("/frames/extract", json=payload)

    assert response.status_code == 200
    data = response.json()
    
    assert data["video_id"] == video_id
    assert data["total_frames_extracted"] == 5
    
    # Frames 0, 1, 2 should be similar (first frame processed, next two skipped)
    # Frames 3, 4 should be different (scene changes, so sent)
    # Total sent should be less than 5
    assert data["frames_sent_to_qwen"] < 5
    assert data["frames_skipped"] > 0
    assert data["reduction_percent"] == round((data["frames_skipped"] / 5) * 100.0, 2)

    # Check report path
    report_path = PROJECT_ROOT / "ADAPTIVE_SAMPLING_REPORT.md"
    assert report_path.exists()
    
    report_content = report_path.read_text(encoding="utf-8")
    assert "ADAPTIVE SAMPLING REPORT" in report_content
    assert str(video_id) in report_content
    assert "Estimated Runtime Savings" in report_content
