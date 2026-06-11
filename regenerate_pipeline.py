import json
import time
from pathlib import Path
from loguru import logger
import traceback

from app.services.event_aggregation import EventAggregationService
from app.services.summary_service import SummaryService
from app.services.search_service import SearchService

video_id = "3a8c4b20-f45a-4334-ba0a-4824b796b750"

def regenerate():
    print(f"--- REGENERATING VIDEO {video_id} ---")
    
    # 1. Event Aggregation
    frames_path = f"data/metadata/{video_id}_frames.json"
    with open(frames_path, "r", encoding="utf-8") as f:
        frames = json.load(f)
    print("Running Event Aggregation...")
    events = EventAggregationService.process_events(video_id, frames)
    print(f"Generated {len(events)} events.")
    
    # 2. Summary Generation
    print("Running Summary Generation...")
    summary = SummaryService.generate_summary(video_id)
    print("Summary generated successfully.")
    
    # 3. Search Indexing
    print("Running Qdrant Reindex...")
    SearchService.index_events(video_id, events)
    print("Qdrant index complete.")
    
    # Also do normal video to verify cross-video validation
    print("\n--- Cross-Video Validation ---")
    # normal traffic
    v_normal = "284e527c-888c-4c80-96c8-3cd7d50731b3"
    try:
        frames_n = json.load(open(f"data/metadata/{v_normal}_frames.json", encoding="utf-8"))
        events_n = EventAggregationService.process_events(v_normal, frames_n)
        print(f"Normal traffic (video {v_normal}): {events_n[0].get('event_type')}")
    except Exception as e:
        print(f"Could not load normal traffic video: {e}")

    print("\n--- FINISHED ---")

if __name__ == "__main__":
    try:
        regenerate()
    except Exception as e:
        traceback.print_exc()
