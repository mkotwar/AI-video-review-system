"""FastAPI router defining endpoints for video frame extraction and Qwen2.5-VL VLM rich metadata generation.
"""

from typing import List
from fastapi import APIRouter, status

from app.schemas.frame import (
    FrameExtractionRequest,
    FrameRichMetadata,
    FrameExtractionResponse,
)
from app.services.frame import FrameExtractionService

router = APIRouter(prefix="/frames", tags=["Frames"])


@router.post(
    "/extract",
    response_model=FrameExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract frames and generate rich VLM metadata",
    description="Sequences through video timeline, extracts exactly 1 JPG frame per second, and triggers Qwen2.5-VL to generate rich semantic metadata.",
)
async def extract_frames(request: FrameExtractionRequest) -> FrameExtractionResponse:
    """HTTP endpoint to execute frame extraction and VLM indexing pipeline for an uploaded video."""
    stats = await FrameExtractionService.extract_frames(request.video_id)
    return FrameExtractionResponse(**stats)


@router.get(
    "/video/{video_id}",
    response_model=List[FrameRichMetadata],
    status_code=status.HTTP_200_OK,
    summary="Get extracted rich frames metadata list",
    description="Retrieves catalog index of VLM rich metadata records for all extracted frames of a given video ID.",
)
def get_frames_metadata(video_id: str) -> List[FrameRichMetadata]:
    """HTTP endpoint to query frame VLM metadata index catalogs."""
    frames_metadata = FrameExtractionService.get_frames(video_id)
    return [FrameRichMetadata(**meta) for meta in frames_metadata]
