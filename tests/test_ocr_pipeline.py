"""Unit tests for OCR extraction, license plate pattern parsing, and timestamp range snippet generation.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.core.utils import format_timestamp_human, calculate_time_snippet
from app.services.ocr import OCRService


def test_timestamp_formatting():
    """Verify seconds format HH:MM:SS conversion utility."""
    # Under a minute
    assert format_timestamp_human(34.0) == "00:00:34"
    assert format_timestamp_human(0.0) == "00:00:00"
    
    # Over a minute
    assert format_timestamp_human(75.2) == "00:01:15"
    
    # Over an hour
    assert format_timestamp_human(3665.0) == "01:01:05"


def test_time_snippet_calculation():
    """Verify calculation of start/end snippet bounds."""
    snippet = calculate_time_snippet(34.0, interval_seconds=1.0)
    
    assert snippet["timestamp_start_seconds"] == 34.0
    assert snippet["timestamp_end_seconds"] == 35.0
    assert snippet["timestamp_start_human"] == "00:00:34"
    assert snippet["timestamp_end_human"] == "00:00:35"


def test_license_plate_matching_regex():
    """Verify that regex matches valid Indian license plates and strips spaces/hyphens."""
    # We can invoke OCRService's license plate parsing logic on clean unique texts.
    # Pattern: r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$"
    
    # Mocking readtext response to test regex parsing via extract_text
    mock_results = [
        ((), "MH 12 AB 1234", 0.99),      # Valid with spaces
        ((), "DL-3C-AA-1111", 0.99),      # Valid with hyphens
        ((), "hr26ct1234", 0.99),         # Valid lowercase
        ((), "RANDOM TEXT", 0.99),        # Invalid text
        ((), "MH123AB1234", 0.99),        # Invalid district digits length
        ((), "MH12AB12345", 0.99),        # Invalid plate digits length
    ]
    
    with patch("easyocr.Reader") as mock_reader_class:
        mock_instance = MagicMock()
        mock_instance.readtext.return_value = mock_results
        mock_reader_class.return_value = mock_instance
        
        # Reset cached reader singleton to use mock
        OCRService._reader = None
        
        result = OCRService.extract_text("dummy_path.jpg")
        
        # Verify detected texts (whitespace normalized, unique, empty strings removed)
        assert "MH 12 AB 1234" in result["detected_text"]
        assert "DL-3C-AA-1111" in result["detected_text"]
        assert "hr26ct1234" in result["detected_text"]
        
        # Verify parsed license plates (cleaned to uppercase and matched)
        assert "MH12AB1234" in result["license_plates"]
        assert "DL3CAA1111" in result["license_plates"]
        assert "HR26CT1234" in result["license_plates"]
        
        # Non-matching plates must not be parsed into license_plates list
        assert "MH123AB1234" not in result["license_plates"]
        assert "MH12AB12345" not in result["license_plates"]
        assert len(result["license_plates"]) == 3


def test_ocr_service_handles_errors_gracefully():
    """Verify OCRService catches exceptions during readtext run and never fails ingestion."""
    with patch("easyocr.Reader") as mock_reader_class:
        mock_instance = MagicMock()
        mock_instance.readtext.side_effect = Exception("CUDA Out of Memory mock error")
        mock_reader_class.return_value = mock_instance
        
        # Reset cached reader singleton to use mock
        OCRService._reader = None
        
        # Act & Assert
        # The service should catch the exception internally, log it, and return empty lists
        result = OCRService.extract_text("dummy_crash_path.jpg")
        
        assert isinstance(result, dict)
        assert result["detected_text"] == []
        assert result["license_plates"] == []
