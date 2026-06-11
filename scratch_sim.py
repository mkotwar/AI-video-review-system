import json
import difflib
import sys
from pathlib import Path

sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
from app.services.event_aggregation import EventAggregationService

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
frames_file = Path(f"c:/Mukul K/vinfo1/video-search-engine/data/metadata/{video_id}_frames.json")

with open(frames_file, "r", encoding="utf-8") as f:
    frames = json.load(f)

print(f"Total frames: {len(frames)}")

threshold = 0.70

for i in range(len(frames) - 1):
    f1 = frames[i]
    f2 = frames[i+1]
    
    cap_sim = difflib.SequenceMatcher(None, f1.get("caption", ""), f2.get("caption", "")).ratio()
    scene_sim = difflib.SequenceMatcher(None, f1.get("scene_type", ""), f2.get("scene_type", "")).ratio()
    
    objs1 = []
    for o in f1.get("objects", []):
        if isinstance(o, dict):
            objs1.append(f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower())
    objs2 = []
    for o in f2.get("objects", []):
        if isinstance(o, dict):
            objs2.append(f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower())
    
    obj_sim = EventAggregationService.jaccard_similarity(objs1, objs2)
    acts_sim = EventAggregationService.jaccard_similarity(f1.get("activities", []), f2.get("activities", []))
    avg_sim = (cap_sim + scene_sim + obj_sim + acts_sim) / 4.0
    
    merge_status = "MERGE" if avg_sim >= threshold else "SPLIT"
    print(f"[{merge_status}] f{i+1:02d}->f{i+2:02d}: Avg={avg_sim:.3f} | Cap={cap_sim:.3f}, Sce={scene_sim:.3f}, Obj={obj_sim:.3f}, Act={acts_sim:.3f}")
