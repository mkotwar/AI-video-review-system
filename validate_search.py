import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/search"
VIDEO_ID = "284e527c-888c-4c80-96c8-3cd7d50731b3"

def search(query, limit=10, score_threshold=0.0, video_ids=None):
    payload = {
        "query": query,
        "limit": limit,
        "score_threshold": score_threshold
    }
    if video_ids:
        payload["video_ids"] = video_ids

    req = urllib.request.Request(
        BASE_URL, 
        data=json.dumps(payload).encode("utf-8"), 
        method="POST", 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode()).get("results", [])
    except Exception as e:
        return []

output_lines = []
def print_out(s):
    output_lines.append(s)

print_out("=== 1. Video Isolation Validation ===")
all_results = search("vehicle", limit=50)
all_video_ids = {r["video_id"] for r in all_results}
print_out(f"Global search returned {len(all_results)} results from videos: {all_video_ids}")

isolated_results = search("vehicle", limit=50, video_ids=[VIDEO_ID])
isolated_video_ids = {r["video_id"] for r in isolated_results}
print_out(f"Isolated search returned {len(isolated_results)} results from videos: {isolated_video_ids}")
if isolated_video_ids == {VIDEO_ID}:
    print_out("[PASS] Video isolation is working.")
else:
    print_out("[FAIL] Video isolation failed.")

print_out("\n=== 2. Confidence Threshold Validation ===")
thresholds = [0.0, 0.2, 0.4, 0.6, 0.8]
for t in thresholds:
    res = search("bus driving on road", limit=20, score_threshold=t, video_ids=[VIDEO_ID])
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
    res = search(q, limit=3, video_ids=[VIDEO_ID])
    for i, r in enumerate(res):
        print_out(f"  #{i+1} [Score: {r['score']:.2f}] {r['description']}")

with open("validation.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

