import sys
import json
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

from app.services.event_aggregation import EventAggregationService
from app.services.search_service import SearchService
from app.core.config import settings
from qdrant_client.models import Filter, FieldCondition, MatchValue

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"

try:
    print(f"Loading frames for {video_id}...")
    with open(frames_path, "r", encoding="utf-8") as f:
        frames = json.load(f)
        
    print(f"Loaded {len(frames)} frames. Reprocessing events...")
    # This automatically overwrites _events.json and the evt_XXX.json files
    new_events = EventAggregationService.process_events(video_id, frames)
    
    print(f"Generated {len(new_events)} aggregated events.")
    
    client = SearchService.get_client()
    print("Deleting old events from Qdrant...")
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
    
    print("Indexing new events into Qdrant...")
    SearchService.index_events(video_id, new_events)
    
    print("Reprocessing and re-indexing complete!")
    
except Exception as e:
    with open("c:/Mukul K/vinfo1/video-search-engine/reprocess_error.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
