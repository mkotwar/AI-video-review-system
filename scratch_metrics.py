import json
from pathlib import Path
import difflib

def jaccard_similarity(list1, list2):
    set1 = set(s.lower().strip() for s in list1 if s.strip())
    set2 = set(s.lower().strip() for s in list2 if s.strip())
    if not set1 and not set2: return 1.0
    if not set1 or not set2: return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def calculate_similarity(frame1, frame2):
    cap1 = frame1.get("caption", "") or ""
    cap2 = frame2.get("caption", "") or ""
    caption_sim = difflib.SequenceMatcher(None, cap1, cap2).ratio()

    scene1 = frame1.get("scene_type", "") or ""
    scene2 = frame2.get("scene_type", "") or ""
    scene_sim = difflib.SequenceMatcher(None, scene1, scene2).ratio()

    objs1 = []
    for o in frame1.get("objects", []):
        if isinstance(o, dict): objs1.append(f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower())
        elif isinstance(o, str): objs1.append(o.lower())
    objs2 = []
    for o in frame2.get("objects", []):
        if isinstance(o, dict): objs2.append(f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower())
        elif isinstance(o, str): objs2.append(o.lower())
    objects_sim = jaccard_similarity(objs1, objs2)

    acts1 = frame1.get("activities", []) or []
    acts2 = frame2.get("activities", []) or []
    activities_sim = jaccard_similarity(acts1, acts2)

    return (caption_sim + scene_sim + objects_sim + activities_sim) / 4.0

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
metadata_dir = Path("c:/Mukul K/vinfo1/video-search-engine/data/metadata")
frames_path = metadata_dir / f"{video_id}_frames.json"
events_path = metadata_dir / f"{video_id}_events.json"

with open(frames_path, "r", encoding="utf-8") as f:
    frames = json.load(f)

with open(events_path, "r", encoding="utf-8") as f:
    events = json.load(f)

with open("c:/Mukul K/vinfo1/video-search-engine/metrics_out.txt", "w", encoding="utf-8") as out:
    out.write("PART 1: EVENT ABSTRACTION VALIDATION\n")
    out.write(f"Total frames: {len(frames)}\n")
    out.write(f"Total events: {len(events)}\n")
    
    total_duration = sum(e["duration_seconds"] for e in events)
    out.write(f"Average event duration: {total_duration / len(events):.2f}s\n")
    
    durations = [e["duration_seconds"] for e in events]
    out.write(f"Longest event: {max(durations):.2f}s\n")
    out.write(f"Shortest event: {min(durations):.2f}s\n")
    
    out.write("\nPART 2: DESCRIPTION QUALITY AUDIT\n")
    for i, e in enumerate(events[:10]):  # print first 10 for review
        out.write(f"Event {i+1}: {e['description']}\n")

    out.write("\nPART 3: FRAGMENTATION THRESHOLD ANALYSIS\n")
    sorted_frames = sorted(frames, key=lambda x: x.get("timestamp_seconds", 0.0))
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
    for t in thresholds:
        groups = []
        current_group = [sorted_frames[0]]
        for i in range(1, len(sorted_frames)):
            f = sorted_frames[i]
            sim = calculate_similarity(current_group[-1], f)
            if sim >= t:
                current_group.append(f)
            else:
                groups.append(current_group)
                current_group = [f]
        if current_group:
            groups.append(current_group)
        
        avg_dur = sum(len(g) for g in groups) / len(groups) # roughly 1 frame = 1 second
        out.write(f"Threshold {t:.2f} -> Events: {len(groups)}, Avg frames/event: {avg_dur:.2f}\n")
