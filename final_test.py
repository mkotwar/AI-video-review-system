import sys
import traceback

with open("FINAL_OUT.txt", "w", encoding="utf-8") as f:
    f.write("STARTING\n")

try:
    sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
    from app.services.search_service import SearchService
    
    VIDEO_ID = "284e527c-888c-4c80-96c8-3cd7d50731b3"
    
    with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
        f.write("IMPORTED\n")
    
    all_results = SearchService.search_events("vehicle", limit=50)
    all_video_ids = {r.get("video_id") for r in all_results}
    
    with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
        f.write(f"Global search returned {len(all_results)} results from videos: {all_video_ids}\n")
        
    isolated_results = SearchService.search_events("vehicle", limit=50, video_ids=[VIDEO_ID])
    isolated_video_ids = {r.get("video_id") for r in isolated_results}
    with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
        f.write(f"Isolated search returned {len(isolated_results)} results from videos: {isolated_video_ids}\n")
        
    thresholds = [0.0, 0.2, 0.4, 0.6, 0.8]
    for t in thresholds:
        res = SearchService.search_events("bus driving on road", limit=20, score_threshold=t, video_ids=[VIDEO_ID])
        with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
            f.write(f"Threshold {t:.1f} -> {len(res)} results\n")
            
    queries = [
        "bus interior dashboard", 
        "pedestrian crossing the street", 
        "white bus"
    ]
    for q in queries:
        with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
            f.write(f"\nQuery: '{q}'\n")
        res = SearchService.search_events(q, limit=3, video_ids=[VIDEO_ID])
        for i, r in enumerate(res):
            with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
                f.write(f"  #{i+1} [Score: {r['score']:.2f}] {r.get('description', '')}\n")

except Exception as e:
    with open("FINAL_OUT.txt", "a", encoding="utf-8") as f:
        f.write(f"ERROR:\n{traceback.format_exc()}\n")
