"""FastAPI router defining endpoints for video uploads, retrieval, and streaming.
"""

from typing import List
from fastapi import APIRouter, File, UploadFile, status, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
import asyncio

from app.schemas.video import VideoMetadataResponse, VideoProcessingStatus
from app.services.video import VideoService
from app.services.frame import FrameExtractionService
from app.services.status_service import JobStatusService

router = APIRouter(prefix="/videos", tags=["Videos"])

def trigger_extraction(video_id: str):
    """Wrapper to run the async extraction in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(FrameExtractionService.extract_frames(video_id))
    except Exception as e:
        from loguru import logger
        logger.exception(f"Background ingestion failed for video {video_id}: {e}")
    finally:
        loop.close()

@router.post(
    "/upload",
    response_model=VideoMetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a video file",
    description="Accepts `.mp4`, `.avi`, or `.mov` format. Streams upload chunk-by-chunk onto storage disks.",
)
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> VideoMetadataResponse:
    """HTTP endpoint to save a video and generate structured indexing metadata."""
    metadata = await VideoService.save_video(file)
    JobStatusService.initialize(metadata["video_id"])
    background_tasks.add_task(trigger_extraction, metadata["video_id"])
    return VideoMetadataResponse(**metadata)


@router.get(
    "/{video_id}",
    response_model=VideoMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get video metadata",
    description="Retrieves the detailed metadata profile for a given UUID4 video identifier.",
)
def get_video_metadata(video_id: str) -> VideoMetadataResponse:
    """HTTP endpoint to fetch video metadata catalog."""
    metadata, _ = VideoService.get_video(video_id)
    return VideoMetadataResponse(**metadata)


@router.get(
    "/{video_id}/status",
    response_model=VideoProcessingStatus,
    status_code=status.HTTP_200_OK,
    summary="Get video processing status",
    description="Retrieves the real-time background processing status and ETA of a video ingestion job.",
)
def get_video_status(video_id: str) -> VideoProcessingStatus:
    """HTTP endpoint to fetch ingestion status."""
    # Ensure video exists
    VideoService.get_video(video_id)
    status_data = JobStatusService.get(video_id)
    return VideoProcessingStatus(**status_data)


@router.get(
    "/{video_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download or stream a video file",
    description="Streams the raw binary video file directly to the client using chunked file serving.",
)
def download_video(video_id: str) -> FileResponse:
    """HTTP endpoint to serve raw video stream."""
    metadata, video_path = VideoService.get_video(video_id)
    filename = metadata.get("filename", f"{video_id}.mp4")

    # Resolve correct MIME types for accepted video formats
    ext = video_path.suffix.lower()
    media_types = {
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=video_path,
        media_type=media_type,
        filename=filename,
    )


@router.get(
    "/{video_id}/stream",
    summary="Stream video with range requests",
    description="Streams video supporting HTTP 206 Partial Content range requests for video seeking.",
)
def stream_video(video_id: str, request: Request) -> Response:
    """HTTP endpoint to serve video stream with range support for players."""
    try:
        metadata, video_path = VideoService.get_video(video_id)
    except Exception:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Video not found")

    if not video_path.exists():
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Video not found")

    file_size = video_path.stat().st_size
    range_header = request.headers.get("range")
    
    ext = video_path.suffix.lower()
    media_types = {
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
    }
    media_type = media_types.get(ext, "video/mp4")

    if range_header:
        # Parse range header e.g., 'bytes=0-1024'
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
        
        # Ensure end is within file size limits
        end = min(end, file_size - 1)
        length = end - start + 1
        
        async def file_iterator():
            with open(video_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk_size = min(1024 * 1024, remaining) # 1MB chunks
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
                    await asyncio.sleep(0.001)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": media_type,
        }
        
        return StreamingResponse(
            file_iterator(),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            headers=headers,
        )
    else:
        # Fallback to standard response if no range requested
        return FileResponse(
            path=video_path,
            media_type=media_type,
            filename=metadata.get("filename", f"{video_id}.mp4"),
            headers={"Accept-Ranges": "bytes"}
        )


@router.get(
    "/",
    response_model=List[VideoMetadataResponse],
    status_code=status.HTTP_200_OK,
    summary="List all videos",
    description="Returns a collection list of metadata definitions for all indexed videos in chronological order.",
)
def list_videos() -> List[VideoMetadataResponse]:
    """HTTP endpoint to catalog all processed videos."""
    videos = VideoService.list_videos()
    return [VideoMetadataResponse(**video) for video in videos]
