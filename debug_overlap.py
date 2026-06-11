import json
from pathlib import Path

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
frames_file = Path(f"c:/Mukul K/vinfo1/video-search-engine/data/metadata/{video_id}_frames.json")

with open(frames_file, "r", encoding="utf-8") as f:
    sorted_frames = json.load(f)

def has_semantic_overlap(group, new_frame):
    acts_group = set()
    for f in group[-3:]:
        for a in f.get("activities", []):
            acts_group.update(w.strip() for w in a.lower().replace('/', ' ').replace(',', ' ').split())
            
    acts_new = set()
    for a in new_frame.get("activities", []):
        acts_new.update(w.strip() for w in a.lower().replace('/', ' ').replace(',', ' ').split())
    
    stop_words = {"in", "on", "at", "movement", "operation", "detected", "the", "a", "an"}
    acts_group -= stop_words
    acts_new -= stop_words
    
    print(f"  Acts Grp: {acts_group}")
    print(f"  Acts New: {acts_new}")
    
    if acts_group.intersection(acts_new):
        print("  -> MATCH via activities")
        return True
        
    def get_core_objects(frames):
        objs = set()
        for f in frames:
            for o in f.get("objects", []):
                if isinstance(o, dict):
                    typ = str(o.get("type", "")).lower()
                    sub = str(o.get("subtype", "")).lower()
                    if any(x in typ for x in ["vehicle", "car", "bus", "truck", "bike"]) or any(x in sub for x in ["vehicle", "car", "bus", "truck", "bike"]):
                        objs.add("vehicle")
                    if any(x in typ for x in ["person", "pedestrian", "driver", "passenger"]) or any(x in sub for x in ["person", "pedestrian", "driver", "passenger"]):
                        objs.add("person")
        return objs
        
    objs_group = get_core_objects(group[-3:])
    objs_new = get_core_objects([new_frame])
    
    print(f"  Objs Grp: {objs_group}")
    print(f"  Objs New: {objs_new}")
    
    if objs_group and objs_new and objs_group.intersection(objs_new):
        print("  -> MATCH via objects")
        return True
        
    print("  -> NO MATCH")
    return False

print("Testing f1 and f2:")
has_semantic_overlap([sorted_frames[0]], sorted_frames[1])

print("\nTesting f2 and f3:")
has_semantic_overlap([sorted_frames[1]], sorted_frames[2])

print("\nTesting f3 and f4:")
has_semantic_overlap([sorted_frames[2]], sorted_frames[3])
