"""Custom domain exceptions for the Video Service layer.

These exceptions cleanly decouple service layer business rules from FastAPI HTTP router levels.
"""


class VideoServiceError(Exception):
    """Base exception class for all errors within the Video Service domain."""

    pass


class VideoValidationError(VideoServiceError):
    """Exception raised when a video file validation fails (e.g. invalid file format)."""

    pass


class VideoNotFoundError(VideoServiceError):
    """Exception raised when the requested video metadata or file cannot be located."""

    pass


class FrameExtractionError(VideoServiceError):
    """Exception raised when frame extraction operations fail (e.g. corrupted files)."""

    pass


class MetadataGenerationError(VideoServiceError):
    """Exception raised when Qwen VLM inference or parsing fails."""

    pass
