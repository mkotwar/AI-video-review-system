import requests
import json
import os

API_BASE = 'http://127.0.0.1:8000'
VIDEOS = {
    'Theft': '03301eee-50a4-4a3a-b5db-11f29b339233',
    'Crash': '733833ea-4569-4b13-91ed-3db2edd8e55f',
    'Fall': 'a629ff6d-ae6a-4fbc-ac3d-bffe9952c8bd',
    'Fire': '00898e90-8ac0-43dd-8a09-0731d05fb590',
    'Normal': 'b32c2588-49bd-4eb6-ac37-f60e3b8f4048'
}

queries = [
    "fall", "crash", "collision", "fire", "theft", "bag snatching", "injury", "police", "arrest", "normal activity"
]

results = {}

for name, vid in VIDEOS.items():
    print(f"Fetching data for {name}...")
    try:
        events = requests.get(f"{API_BASE}/api/v1/videos/{vid}/events").json()
        summary = requests.get(f"{API_BASE}/api/v1/videos/{vid}/summary").json()
        report = requests.get(f"{API_BASE}/api/v1/videos/{vid}/report").json()
        results[name] = {
            'events': events,
            'summary': summary,
            'report': report
        }
    except Exception as e:
        print(f"Error fetching {name}: {e}")

print("Fetching search results...")
search_results = {}
for q in queries:
    try:
        res = requests.post(f"{API_BASE}/api/v1/search", json={"query": q, "limit": 1, "score_threshold": 0}).json()
        if 'results' in res and len(res['results']) > 0:
            top = res['results'][0]
            search_results[q] = {
                'video_id': top['video_id'],
                'score': top['score'],
                'description': top['description'],
                'event_type': top['event_type']
            }
        else:
            search_results[q] = "No results"
    except Exception as e:
        print(f"Error searching {q}: {e}")
        
results['searches'] = search_results

out_path = r'c:\Mukul K\vinfo1\video-search-engine\audit_data.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Saved to {out_path}")
