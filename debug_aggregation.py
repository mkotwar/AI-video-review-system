import json
import sys
from pathlib import Path

sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
from app.services.event_aggregation import EventAggregationService

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
frames_file = Path(f"c:/Mukul K/vinfo1/video-search-engine/data/metadata/{video_id}_frames.json")

with open(frames_file, "r", encoding="utf-8") as f:
    frames = json.load(f)

print(f"Total frames loaded: {len(frames)}")
print("Running modified aggregation...")

events = EventAggregationService.process_events(video_id, frames)

print(f"Total events generated: {len(events)}")
