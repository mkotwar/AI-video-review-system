import json
from pathlib import Path
from app.core.config import settings
from app.services.search_service import SearchService

for path in settings.METADATA_DIR.glob("*_events_v2.json"):
    video_id = path.name.replace("_events_v2.json", "")
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)
    
    modified = False
    events_dir = settings.EVENTS_DIR / video_id
    
    for e in events:
        if "thumbnail_path" not in e or not e["thumbnail_path"]:
            event_id = e["event_id"]
            event_json_path = events_dir / f"{event_id}.json"
            if event_json_path.exists():
                with open(event_json_path, "r", encoding="utf-8") as ef:
                    original_event = json.load(ef)
                source_frames = original_event.get("source_frames", [])
                if source_frames:
                    frame_id = source_frames[0]
                    e["thumbnail_path"] = f"/api/v1/events/{video_id}/thumbnail/{frame_id}"
                    modified = True

    if modified:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4)
        print(f"Patched {path}")
        SearchService.index_events(video_id, events)

print("Patching complete.")
