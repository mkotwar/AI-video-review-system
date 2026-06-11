"""Core utility functions for the AI Video Search Engine.
"""

def format_timestamp_human(seconds: float) -> str:
    """Converts float seconds to playback timestamp formatted as HH:MM:SS."""
    total_seconds = int(round(seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def calculate_time_snippet(timestamp_seconds: float, interval_seconds: float = 1.0) -> dict:
    """Calculates start and end timestamps and their human-readable HH:MM:SS formats.

    Args:
        timestamp_seconds: The playback timestamp in seconds (start of the interval).
        interval_seconds: Sampling interval length in seconds (default is 1.0).

    Returns:
        dict: A dictionary containing:
            - timestamp_start_seconds (float)
            - timestamp_end_seconds (float)
            - timestamp_start_human (str)
            - timestamp_end_human (str)
    """
    start_sec = float(timestamp_seconds)
    end_sec = start_sec + float(interval_seconds)
    return {
        "timestamp_start_seconds": start_sec,
        "timestamp_end_seconds": end_sec,
        "timestamp_start_human": format_timestamp_human(start_sec),
        "timestamp_end_human": format_timestamp_human(end_sec),
    }
