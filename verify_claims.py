import json
import os
import glob
from pathlib import Path
import sys

sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")
from app.services.search_service import SearchService
from app.services.summary_service import SummaryService

base_dir = "c:/Mukul K/vinfo1/video-search-engine"
data_dir = os.path.join(base_dir, "data")
events_dir = os.path.join(data_dir, "events")

with open(os.path.join(base_dir, "claims_output.txt"), "w", encoding="utf-8") as out:
    def print_out(text):
        out.write(text + "\n")
        
    print_out("========== CLAIM 1: Event Aggregation ==========")
    dirs = [d for d in os.listdir(events_dir) if os.path.isdir(os.path.join(events_dir, d))]
    recent_dirs = dirs[:3]

    for d in recent_dirs:
        events_files = glob.glob(os.path.join(events_dir, d, "*.json"))
        if not events_files: continue
        
        with open(events_files[0], "r", encoding="utf-8") as f:
            event_data = json.load(f)
            
        unified = event_data.get("unified_text", "")
        words = unified.split()
        if words:
            dupe_ratio = len(words) / max(1, len(set(words)))
            print_out(f"Video {d} | Event: {os.path.basename(events_files[0])}")
            print_out(f"  Unified Text Length: {len(unified)} characters, {len(words)} words.")
            print_out(f"  Duplication Ratio: {dupe_ratio:.2f} (Words / Unique Words)")


    print_out("\n========== CLAIM 2: Accident Detection ==========")
    accident_events = []
    for d in dirs:
        for f_path in glob.glob(os.path.join(events_dir, d, "*.json")):
            with open(f_path, "r", encoding="utf-8") as f:
                evt = json.load(f)
                if evt.get("event_type") == "collision_or_accident":
                    accident_events.append(evt)

    if accident_events:
        evt = accident_events[0]
        print_out("Found Accident Event!")
        print_out(f"1. Does collision_or_accident appear? Yes, event_type: {evt.get('event_type')}")
        print_out(f"2. Does severity appear? Yes, severity: {evt.get('event_severity')}")
        print_out(f"3. Does summary mention accident? Summary: {evt.get('summary')}")
    else:
        print_out("No accident events found in current DB.")


    print_out("\n========== CLAIM 3: Search Precision ==========")
    queries = ["accident", "collision", "vehicle", "person", "fall"]
    for q in queries:
        try:
            results = SearchService.search_events(query=q, limit=3, score_threshold=0.0)
            print_out(f"Query: '{q}' -> Found {len(results)} results.")
            for i, r in enumerate(results):
                print_out(f"   [{i+1}] Score: {r.get('score', 0):.3f} | Desc: {r.get('description', '')[:60]}...")
        except Exception as e:
            print_out(f"Query '{q}' failed: {e}")

    print_out("\n========== CLAIM 4: Summary Quality ==========")
    for d in recent_dirs:
        try:
            summary = SummaryService.generate_summary(d)
            print_out(f"Video {d} Overview: {summary.overview[:100]}...")
        except Exception as e:
            print_out(f"Summary for {d} failed: {e}")
