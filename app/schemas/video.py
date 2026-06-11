"""Pydantic schemas for structural validation of Video objects.
"""

from pydantic import BaseModel, Field


class VideoMetadataResponse(BaseModel):
    """Schema representing structural metadata of an indexed video."""

    video_id: str = Field(
        ...,
        description="Unique UUID4 identifier assigned to the video.",
        examples=["479a951c-8b89-4976-b9bd-7c98c1992015"],
    )
    filename: str = Field(
        ...,
        description="Original client filename of the uploaded video.",
        examples=["sample_presentation.mp4"],
    )
    upload_time: str = Field(
        ...,
        description="ISO 8601 formatted UTC timestamp recording the upload moment.",
        examples=["2026-06-02T12:31:00Z"],
    )
    file_size: int = Field(
        ...,
        description="Total size of the video file in bytes.",
        examples=[1048576],
    )


class VideoProcessingStatus(BaseModel):
    """Schema representing the real-time background processing status of a video."""
    video_id: str
    status: str
    current_step: str
    total_frames: int
    processed_frames: int
    events_generated: int
    progress_percent: float
    estimated_time_remaining: float
