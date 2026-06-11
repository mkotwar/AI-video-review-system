import json
import os
import sys

def main():
    video_id = "3a8c4b20-f45a-4334-ba0a-4824b796b750"
    base_dir = "c:/Mukul K/vinfo1/video-search-engine/data"
    
    print("--- STEP 4: EVENT CATALOG VERIFICATION ---")
    path = f"{base_dir}/metadata/{video_id}_events_v2.json"
    events = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
        if events:
            e = events[0]
            print(f"event_id: {e.get('event_id')}")
            print(f"event_type: {e.get('event_type')}")
            print(f"description: {e.get('description')}")
            print(f"event_severity: {e.get('event_severity')}")
            print(f"behavioral_flags: {e.get('behavioral_flags')}")
    else:
        print("events_v2.json not found")
        
    print("\n--- STEP 5: TIMELINE VERIFICATION ---")
    if events:
        for e in events:
            print(f"{e.get('start_time')} - {e.get('end_time')} | {e.get('event_type')} | {e.get('description')}")
            
    print("\n--- STEP 6: NOTABLE EVENTS VERIFICATION ---")
    sum_path = f"{base_dir}/metadata/{video_id}_summary.json"
    summary = {}
    if os.path.exists(sum_path):
        with open(sum_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        print(json.dumps(summary.get("notable_events", []), indent=2))
    else:
        print("summary.json not found")
        
    print("\n--- STEP 7: AI OVERVIEW VERIFICATION ---")
    if os.path.exists(sum_path):
        print(summary.get("ai_overview", "No overview"))
        
    print("\n--- STEP 8: SEARCH VERIFICATION ---")
    try:
        from app.services.search_service import SearchService
        queries = ["accident", "collision", "crash", "damaged vehicle"]
        for q in queries:
            print(f"\nQuery: {q}")
            results = SearchService.search_events(query=q, limit=3, video_ids=[video_id])
            for i, r in enumerate(results):
                print(f"Rank {i+1} | Confidence: {r['score']:.4f} | Event: {r['event']['event_type']} | Desc: {r['event']['description']}")
    except Exception as e:
        print(f"SearchService failed: {e}")

if __name__ == "__main__":
    sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
    main()
