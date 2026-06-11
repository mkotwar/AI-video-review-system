"""Video service layer managing video files, chunked local streaming, and metadata.
"""

import json
import uuid
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
from fastapi import UploadFile
from loguru import logger

from app.core.config import settings
from app.core.exceptions import VideoValidationError, VideoNotFoundError


class VideoService:
    """Service class encapsulating business logic for video uploads, storage, and retrieval."""

    ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
    UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    @classmethod
    def _validate_video_id(cls, video_id: str) -> None:
        """Sanitize and validate video ID structure to prevent directory traversal attempts."""
        if not cls.UUID_REGEX.match(video_id):
            logger.warning(f"Malicious or malformed video ID requested: {video_id}")
            raise VideoValidationError("Invalid video ID format.")

    @classmethod
    async def save_video(cls, file: UploadFile) -> Dict[str, Any]:
        """Validates, streams, and stores a video file and its metadata.

        Args:
            file: The Starlette UploadFile object.

        Returns:
            dict: The saved video's metadata schema.

        Raises:
            VideoValidationError: If extension or size checks fail.
        """
        start_time = time.perf_counter()
        if not file.filename:
            raise VideoValidationError("Filename cannot be empty.")

        # 1. Parse and validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            logger.warning(f"File upload rejected. Invalid extension: {ext}")
            raise VideoValidationError(
                f"Unsupported video format '{ext}'. Allowed extensions: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        # 2. Generate a secure unique video_id
        video_id = str(uuid.uuid4())
        video_filename = f"{video_id}{ext}"
        video_path = settings.VIDEOS_DIR / video_filename

        logger.info(f"Initiating video file save pipeline for original file: {file.filename} -> ID: {video_id}")

        # 3. Stream upload contents to local storage in chunks (1MB) to limit memory overhead
        file_size = 0
        chunk_size = 1024 * 1024  # 1 MB

        try:
            with open(video_path, "wb") as buffer:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    buffer.write(chunk)
                    file_size += len(chunk)

            # Prevent empty file uploads
            if file_size == 0:
                # Cleanup empty file
                if video_path.exists():
                    video_path.unlink()
                raise VideoValidationError("Uploaded file is empty.")

        except Exception as exc:
            # Ensure cleanup on errors
            if video_path.exists():
                video_path.unlink()
            logger.exception(f"Disk write failure during video storage stream for ID {video_id}")
            raise exc

        # 4. Formulate the required metadata structure
        upload_duration_ms = (time.perf_counter() - start_time) * 1000.0
        upload_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        metadata = {
            "video_id": video_id,
            "filename": file.filename,
            "upload_time": upload_time,
            "file_size": file_size,
            "upload_duration_ms": round(upload_duration_ms, 2),
        }

        # 5. Write metadata structure to json file
        metadata_path = settings.METADATA_DIR / f"{video_id}.json"
        try:
            with open(metadata_path, "w", encoding="utf-8") as meta_file:
                json.dump(metadata, meta_file, indent=4)
        except Exception as exc:
            # Cleanup stored video if metadata write fails
            if video_path.exists():
                video_path.unlink()
            logger.exception(f"File write failure during metadata storage for ID {video_id}")
            raise exc

        # 6. Structured Logging
        logger.info(f"Successfully saved raw video to: {video_path}")

        # Log directly to metadata log sink
        meta_logger = logger.bind(context="metadata")
        meta_logger.info(
            f"Successfully processed upload and stored metadata | "
            f"video_id={video_id} | filename={file.filename} | "
            f"size_bytes={file_size} | path={video_path}"
        )

        return metadata

    @classmethod
    def get_video(cls, video_id: str) -> Tuple[Dict[str, Any], Path]:
        """Retrieves metadata and storage file path for a specific video ID.

        Args:
            video_id: Unique UUID4 string representing the video.

        Returns:
            tuple: (metadata_dict, video_file_path)

        Raises:
            VideoValidationError: If ID format is malformed.
            VideoNotFoundError: If file or metadata does not exist.
        """
        cls._validate_video_id(video_id)

        metadata_path = settings.METADATA_DIR / f"{video_id}.json"

        # Check metadata existence
        if not metadata_path.exists():
            logger.warning(f"Metadata lookup failed. Video ID does not exist: {video_id}")
            raise VideoNotFoundError(f"Video with ID '{video_id}' not found.")

        # Load metadata
        try:
            with open(metadata_path, "r", encoding="utf-8") as meta_file:
                metadata = json.load(meta_file)
        except Exception as exc:
            logger.exception(f"Read failure on metadata file: {metadata_path}")
            raise VideoNotFoundError("Corrupted or unreadable metadata.")

        # Derive raw video extension and path
        orig_filename = metadata.get("filename", "")
        ext = Path(orig_filename).suffix.lower()
        video_path = settings.VIDEOS_DIR / f"{video_id}{ext}"

        if not video_path.exists():
            logger.warning(f"Video file missing on disk for existing metadata: {video_path}")
            raise VideoNotFoundError(f"Video file for ID '{video_id}' is missing on storage.")

        return metadata, video_path

    @classmethod
    def list_videos(cls) -> List[Dict[str, Any]]:
        """Scans the metadata storage and collects metadata catalogs for all registered videos.

        Returns:
            list: List of metadata dictionaries.
        """
        videos_list: List[Dict[str, Any]] = []

        # Iterate all json files in metadata storage
        for path in settings.METADATA_DIR.glob("*.json"):
            # Skip non-uuid format files if any exist
            stem = path.stem
            if not cls.UUID_REGEX.match(stem):
                continue

            try:
                with open(path, "r", encoding="utf-8") as meta_file:
                    metadata = json.load(meta_file)
                    videos_list.append(metadata)
            except Exception:
                logger.warning(f"Failed to read metadata file: {path}. Skipping record.")

        # Sort by upload_time descending
        videos_list.sort(key=lambda x: x.get("upload_time", ""), reverse=True)
        return videos_list
