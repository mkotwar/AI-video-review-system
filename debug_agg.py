import json
import traceback
try:
    from app.services.event_aggregation import EventAggregationService
    frames = json.load(open("data/metadata/a48b4d08-7e3c-4aa3-a801-0756875508b8_frames.json", encoding="utf-8"))
    events = EventAggregationService.process_events("test_video_id", frames)
    with open("debug_out.txt", "w") as f:
        f.write(f"Number of events: {len(events)}\n")
        for i, e in enumerate(events):
            f.write(f"Event {i}: duration = {e['duration_seconds']}, start = {e['start_time']}, end = {e['end_time']}\n")
except Exception as e:
    with open("debug_out.txt", "w") as f:
        f.write("ERROR:\n" + traceback.format_exc())
