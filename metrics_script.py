import json, urllib.request, urllib.parse, sys
from pathlib import Path

video_id = "284e527c-888c-4c80-96c8-3cd7d50731b3"
base = Path(r"c:\Mukul K\vinfo1\video-search-engine")

res = {}

# Part 2: Frames extraction
f_path = base / "data" / "metadata" / f"{video_id}_frames.json"
if f_path.exists():
    with open(f_path, encoding='utf-8') as f:
        frames = json.load(f)
        res['Frames'] = len(frames)
        res['With Activities'] = sum(1 for x in frames if x.get('activities'))
        sources = {'caption':0, 'attributes':0, 'keywords':0, 'none':0, 'null':0}
        for x in frames:
            s = x.get('activity_recovery_source')
            if s is None:
                sources['null'] += 1
            else:
                sources[s] = sources.get(s, 0) + 1
        res['Sources'] = sources

# Part 5: Summary
try:
    u = urllib.request.urlopen(f'http://localhost:8000/api/v1/videos/{video_id}/summary')
    res['Summary'] = json.loads(u.read())
except Exception as e:
    res['Summary Error'] = str(e)

# Part 6: Semantic search
queries = ["parked vehicle", "moving vehicle", "walking person", "crossing road", "motorcycle", "person", "vehicle"]
searches = {}
for q in queries:
    payload = json.dumps({"query": q, "limit": 3, "video_ids": [video_id], "score_threshold": 0.5}).encode('utf-8')
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/search", data=payload, method="POST", headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as u:
            searches[q] = json.loads(u.read())
    except Exception as e:
        searches[q] = {"error": str(e)}
res['Searches'] = searches

# Part 7: Thresholds
thresholds = {}
for t in [0.9, 0.8, 0.7, 0.6, 0.5]:
    payload = json.dumps({"query": "vehicle", "limit": 100, "video_ids": [video_id], "score_threshold": t}).encode('utf-8')
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/search", data=payload, method="POST", headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as u:
            thresholds[t] = len(json.loads(u.read()).get("results", []))
    except Exception as e:
        thresholds[t] = str(e)
res['Thresholds'] = thresholds

with open(base / "metrics.json", "w") as f:
    json.dump(res, f, indent=2)
