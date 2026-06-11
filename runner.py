import sys
import json
import urllib.request
from pathlib import Path

with open("c:/Mukul K/vinfo1/video-search-engine/report.txt", "w", encoding="utf-8") as out:
    sys.stdout = out
    video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
    base_dir = Path("c:/Mukul K/vinfo1/video-search-engine")
    
    print("--- PART 1: VIDEO PROCESSING AUDIT ---")
    meta_path = base_dir / "data" / "metadata" / f"{video_id}.json"
    if meta_path.exists():
        with open(meta_path) as f:
            print("Base Metadata:", f.read())
            
    frames_dir = base_dir / "data" / "metadata" / video_id
    frame_files = list(frames_dir.glob("*.json"))
    print(f"Frames extracted/analyzed: {len(frame_files)}")
    
    frames_json = base_dir / "data" / "metadata" / f"{video_id}_frames.json"
    events_json = base_dir / "data" / "metadata" / f"{video_id}_events.json"
    print("Exists _frames.json?", frames_json.exists())
    print("Exists _events.json?", events_json.exists())

    print("\n--- PART 2: ACTIVITY EXTRACTION AUDIT ---")
    sys.path.insert(0, str(base_dir))
    from scripts.measure_activity_recovery import load_frames, measure_video, print_report
    if frames_json.exists():
        frames = load_frames(frames_json)
        res = measure_video(video_id, frames)
        print_report(res)
    else:
        print("frames_json not found.")

    print("\n--- PART 3: EVENT AGGREGATION AUDIT ---")
    if events_json.exists():
        with open(events_json, encoding="utf-8") as f:
            events = json.load(f)
            print("Total events:", len(events))
            counts = {}
            for e in events:
                t = e.get("event_type", "unknown")
                counts[t] = counts.get(t, 0) + 1
            print("Event type counts:", counts)
            print("\nSample Events:")
            for e in events[:2]:
                print(e)
    else:
        print("events_json not found.")
        
    print("\n--- PART 4: EVENT DESCRIPTION QUALITY ---")
    if events_json.exists():
        for i, e in enumerate(events[:10]):
            print(f"Desc {i}: {e.get('description')}")
            
    print("\n--- PART 5: SUMMARY QUALITY AUDIT ---")
    url = f"http://localhost:8000/api/v1/videos/{video_id}/summary"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as response:
            print("Summary API Response Code:", response.getcode())
            print(json.dumps(json.loads(response.read()), indent=2))
    except Exception as e:
        print("Error calling Summary API:", e)
        
    print("\n--- PART 6: SEMANTIC SEARCH VALIDATION ---")
    queries = ["parked vehicle", "moving vehicle", "walking person", "crossing road", "motorcycle", "person", "vehicle"]
    for q in queries:
        print(f"\nQuery: {q}")
        search_payload = json.dumps({"query": q, "limit": 3, "video_ids": [video_id], "score_threshold": 0.5}).encode('utf-8')
        try:
            req = urllib.request.Request("http://localhost:8000/api/v1/search", data=search_payload, method="POST", headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read())
                for r in res.get("results", []):
                    print(f"  Score: {r['score']:.4f} | Event: {r['event']['event_type']} | Desc: {r['event']['description']}")
        except Exception as e:
            print("Search error:", e)

    print("\n--- PART 7: Threshold Test ---")
    for t in [0.9, 0.8, 0.7, 0.6, 0.5]:
        print(f"\nThreshold: {t}")
        search_payload = json.dumps({"query": "vehicle", "limit": 100, "video_ids": [video_id], "score_threshold": t}).encode('utf-8')
        try:
            req = urllib.request.Request("http://localhost:8000/api/v1/search", data=search_payload, method="POST", headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read())
                print(f"  Results returned: {len(res.get('results', []))}")
                if len(res.get('results', [])) > 0:
                     print(f"  Top Score: {res.get('results')[0]['score']:.4f}")
        except Exception as e:
            print("Search error:", e)
