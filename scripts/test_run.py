import json
import traceback
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

try:
    from app.services.event_aggregation import EventAggregationService
    from app.core.config import settings

    video_id = "1aca8e7b-9f5d-4045-930b-cc87b7e580bd"
    frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"
    
    with open(frames_path, "r", encoding="utf-8") as f:
        frames = json.load(f)
        
    events = EventAggregationService.process_events(video_id, frames)
    
    out_path = r"c:\Mukul K\vinfo1\video-search-engine\output_test.txt"
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"Event Count: {len(events)}\n")
        if events:
            avg_dur = sum(e["duration_seconds"] for e in events) / len(events)
            out_f.write(f"Average Duration: {avg_dur:.2f}s\n\n")
        for e in events:
            out_f.write(f"{e['event_id']} ({e['duration_seconds']}s): {e['summary']}\n")
            
except Exception as e:
    out_path = r"c:\Mukul K\vinfo1\video-search-engine\output_test.txt"
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"ERROR: {e}\n")
        traceback.print_exc(file=out_f)
