import sys
import json
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

# ONLY import EventAggregationService to avoid PyTorch crashes
from app.services.event_aggregation import EventAggregationService
from app.core.config import settings

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"

try:
    with open(frames_path, "r", encoding="utf-8") as f:
        frames = json.load(f)
        
    print(f"Loaded {len(frames)} frames. Reprocessing events...")
    
    # Process events (this will overwrite _events.json)
    new_events = EventAggregationService.process_events(video_id, frames)
    
    print(f"Successfully generated and saved {len(new_events)} aggregated events.")
    
except Exception as e:
    print(f"ERROR: {traceback.format_exc()}")
