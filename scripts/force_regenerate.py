import os
import sys
import traceback
import json
from pathlib import Path

sys.path.insert(0, str(Path(r"c:\Mukul K\vinfo1\video-search-engine")))

def run():
    try:
        from app.core.config import settings
        from app.services.event_aggregation import EventAggregationService

        video_id = "1398ebb1-26f1-4eac-9fa9-34a7480b70e1"
        frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"
        
        with open("regen_log.txt", "w") as log_f:
            log_f.write(f"Checking path: {frames_path}\n")
            if not frames_path.exists():
                log_f.write("Not found.\n")
                return
            
            with open(frames_path, "r", encoding="utf-8") as f:
                frames_metadata = json.load(f)
            
            log_f.write(f"Loaded {len(frames_metadata)} frames.\n")
            events = EventAggregationService.process_events(video_id, frames_metadata)
            log_f.write(f"Generated {len(events)} events.\n")
            log_f.write("Done.\n")
    except Exception as e:
        with open("regen_log.txt", "a") as log_f:
            log_f.write(traceback.format_exc())

if __name__ == "__main__":
    run()
