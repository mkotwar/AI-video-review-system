"""Service to manage background processing job statuses."""

import json
import time
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings

class JobStatusService:
    """Manages file-based status tracking for video metadata ingestion jobs."""
    
    @classmethod
    def get_status_path(cls, video_id: str) -> Path:
        """Returns the path to the status JSON file for a given video ID."""
        return settings.METADATA_DIR / f"{video_id}_status.json"

    @classmethod
    def initialize(cls, video_id: str) -> None:
        """Creates an initial status file for a new job."""
        path = cls.get_status_path(video_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        status_data = {
            "video_id": video_id,
            "status": "processing",
            "current_step": "Pending",
            "total_frames": 0,
            "processed_frames": 0,
            "events_generated": 0,
            "progress_percent": 0.0,
            "estimated_time_remaining": 0.0,
            "start_time": time.time(),
            "vlm_start_time": None
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(status_data, f)

    @classmethod
    def get(cls, video_id: str) -> Dict[str, Any]:
        """Retrieves the current job status."""
        path = cls.get_status_path(video_id)
        if not path.exists():
            return {
                "video_id": video_id,
                "status": "unknown",
                "current_step": "Status file not found",
                "total_frames": 0,
                "processed_frames": 0,
                "events_generated": 0,
                "progress_percent": 0.0,
                "estimated_time_remaining": 0.0
            }
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "video_id": video_id,
                "status": "processing",
                "current_step": "Reading status...",
                "total_frames": 0,
                "processed_frames": 0,
                "events_generated": 0,
                "progress_percent": 0.0,
                "estimated_time_remaining": 0.0
            }

    @classmethod
    def update(cls, video_id: str, **kwargs) -> None:
        """Updates specific fields in the job status."""
        path = cls.get_status_path(video_id)
        if not path.exists():
            cls.initialize(video_id)
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return # Skip update if file is corrupted
            
        data.update(kwargs)
        
        # Calculate ETA dynamically based on overall progress
        progress = data.get("progress_percent", 0.0)
        if progress > 0.0 and progress < 100.0:
            start_time = data.get("start_time", time.time())
            elapsed = time.time() - start_time
            if elapsed > 0:
                total_estimated_time = elapsed / (progress / 100.0)
                remaining = max(0.0, total_estimated_time - elapsed)
                data["estimated_time_remaining"] = round(remaining, 1)
        elif progress >= 100.0:
            data["estimated_time_remaining"] = 0.0
            
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass # Ignore write collisions
