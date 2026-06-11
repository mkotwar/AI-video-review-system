import sys
import traceback

with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "w", encoding="utf-8") as f:
    f.write("STARTING SCRIPT\n")

try:
    import json
    from pathlib import Path

    # Add project root to path
    sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write("IMPORTING SERVICES\n")

    from app.services.event_aggregation import EventAggregationService
    from app.services.search_service import SearchService
    from app.core.config import settings
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write("IMPORTS SUCCESSFUL\n")

    video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
    frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"

    with open(frames_path, "r", encoding="utf-8") as f:
        frames = json.load(f)
        
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write(f"LOADED {len(frames)} FRAMES\n")

    new_events = EventAggregationService.process_events(video_id, frames)
    
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write(f"GENERATED {len(new_events)} AGGREGATED EVENTS\n")
    
    client = SearchService.get_client()
    
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write("DELETING OLD EVENTS\n")

    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="video_id",
                    match=MatchValue(value=video_id)
                )
            ]
        )
    )
    
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write("INDEXING NEW EVENTS\n")

    SearchService.index_events(video_id, new_events)
    
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write("COMPLETED SUCCESSFULLY\n")
    
except Exception as e:
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_trace.txt", "a", encoding="utf-8") as f:
        f.write(f"ERROR: {traceback.format_exc()}\n")
