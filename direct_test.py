import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

from app.services.search_service import SearchService

VIDEO_ID = "284e527c-888c-4c80-96c8-3cd7d50731b3"

output_lines = []
def print_out(s):
    output_lines.append(s)

import traceback
try:

print_out("=== 1. Video Isolation Validation ===")
all_results = SearchService.search_events("vehicle", limit=50)
all_video_ids = {r.get("video_id") for r in all_results}
print_out(f"Global search returned {len(all_results)} results from videos: {all_video_ids}")

isolated_results = SearchService.search_events("vehicle", limit=50, video_ids=[VIDEO_ID])
isolated_video_ids = {r.get("video_id") for r in isolated_results}
print_out(f"Isolated search returned {len(isolated_results)} results from videos: {isolated_video_ids}")
if isolated_video_ids == {VIDEO_ID}:
    print_out("[PASS] Video isolation is working.")
else:
    print_out("[FAIL] Video isolation failed.")

print_out("\n=== 2. Confidence Threshold Validation ===")
thresholds = [0.0, 0.2, 0.4, 0.6, 0.8]
for t in thresholds:
    res = SearchService.search_events("bus driving on road", limit=20, score_threshold=t, video_ids=[VIDEO_ID])
    print_out(f"Threshold {t:.1f} -> {len(res)} results")
    if res:
        print_out(f"  Highest score: {res[0]['score']:.2f}, Lowest score: {res[-1]['score']:.2f}")

print_out("\n=== 3. Search Relevance & Precision/Recall ===")
queries = [
    "bus interior dashboard", 
    "pedestrian crossing the street", 
    "white bus",
    "passenger watching screen"
]

for q in queries:
    print_out(f"\nQuery: '{q}'")
    res = SearchService.search_events(q, limit=3, video_ids=[VIDEO_ID])
    for i, r in enumerate(res):
        print_out(f"  #{i+1} [Score: {r['score']:.2f}] {r.get('description', '')}")

except Exception as e:
    output_lines.append(f"\nERROR: {traceback.format_exc()}")

with open(r"C:\Users\Vinfocom\.gemini\antigravity-ide\brain\43a62129-4471-4ddb-8227-31e3a3227408\validation_results.md", "w", encoding="utf-8") as f:
    f.write("# Validation Results\n\n```text\n")
    f.write("\n".join(output_lines))
    f.write("\n```")


