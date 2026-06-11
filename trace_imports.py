print("1. core.config", flush=True)
from app.core.config import settings

print("2. core.logging", flush=True)
from app.core.logging import setup_logging

print("3. core.exceptions", flush=True)
from app.core.exceptions import VideoValidationError

print("4. api.videos", flush=True)
from app.api.videos import router as videos_router

print("5. api.frames", flush=True)
from app.api.frames import router as frames_router

print("6. api.summary", flush=True)
from app.api.summary import router as summary_router

print("7. api.search", flush=True)
from app.api.search import router as search_router

print("All imports done!", flush=True)
