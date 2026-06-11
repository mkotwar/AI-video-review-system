import json
import os
import sys

def main():
    video_id = "3a8c4b20-f45a-4334-ba0a-4824b796b750"
    base_dir = "c:/Mukul K/vinfo1/video-search-engine/data"
    
    out = []
    out.append("--- STEP 4: EVENT CATALOG VERIFICATION ---")
    path = f"{base_dir}/metadata/{video_id}_events_v2.json"
    events = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
        if events:
            e = events[0]
            out.append(f"event_id: {e.get('event_id')}")
            out.append(f"event_type: {e.get('event_type')}")
            out.append(f"description: {e.get('description')}")
            out.append(f"event_severity: {e.get('event_severity')}")
            out.append(f"behavioral_flags: {e.get('behavioral_flags')}")
    else:
        out.append("events_v2.json not found")
        
    out.append("\n--- STEP 5: TIMELINE VERIFICATION ---")
    if events:
        for e in events:
            out.append(f"{e.get('start_time')} - {e.get('end_time')} | {e.get('event_type')} | {e.get('description')}")
            
    out.append("\n--- STEP 6: NOTABLE EVENTS VERIFICATION ---")
    sum_path = f"{base_dir}/metadata/{video_id}_summary.json"
    summary = {}
    if os.path.exists(sum_path):
        with open(sum_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        out.append(json.dumps(summary.get("notable_events", []), indent=2))
    else:
        out.append("summary.json not found")
        
    out.append("\n--- STEP 7: AI OVERVIEW VERIFICATION ---")
    if os.path.exists(sum_path):
        out.append(summary.get("ai_overview", "No overview"))
        
    out.append("\n--- STEP 8: SEARCH VERIFICATION ---")
    try:
        from app.services.search_service import SearchService
        queries = ["accident", "collision", "crash", "damaged vehicle"]
        for q in queries:
            out.append(f"\nQuery: {q}")
            results = SearchService.search_events(query=q, limit=3, video_ids=[video_id])
            for i, r in enumerate(results):
                out.append(f"Rank {i+1} | Confidence: {r['score']:.4f} | Event: {r['event']['event_type']} | Desc: {r['event']['description']}")
    except Exception as e:
        out.append(f"SearchService failed: {e}")

    with open("c:/Mukul K/vinfo1/video-search-engine/output_val.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
    main()
