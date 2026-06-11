"""Pytest configuration and global fixtures.
"""

import pytest
from app.core.config import settings

# Force mock model mode globally during tests to prevent VLM loading and ensure fast execution
settings.MOCK_MODEL = True
