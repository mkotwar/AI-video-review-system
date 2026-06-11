import json
import sys
import traceback
sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

try:
    from app.services.event_aggregation import EventAggregationService
    video_id = "3a8c4b20-f45a-4334-ba0a-4824b796b750"
    frames = json.load(open(f"c:/Mukul K/vinfo1/video-search-engine/data/metadata/{video_id}_frames.json", encoding="utf-8"))
    events = EventAggregationService.process_events(video_id, frames)
    with open("c:/Mukul K/vinfo1/video-search-engine/test_agg_out.txt", "w", encoding="utf-8") as f:
        f.write(f"SUCCESS: {len(events)} events generated.\n")
except Exception as e:
    with open("c:/Mukul K/vinfo1/video-search-engine/test_agg_out.txt", "w", encoding="utf-8") as f:
        f.write("ERROR:\n" + traceback.format_exc())
