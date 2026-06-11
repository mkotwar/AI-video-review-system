import urllib.request
import json

url = "http://localhost:8000/api/v1/search"
queries = ["bus", "driver", "moving vehicle", "road", "passenger", "vehicle"]

print("--- TESTING SEARCH API ---")

for q in queries:
    payload = json.dumps({
        "query": q,
        "limit": 10,
        "score_threshold": 0.0
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            results = res.get("results", [])
            print(f"\nQuery: '{q}' -> Found {len(results)} results")
            if results:
                # Print top 3 scores
                top_scores = [round(r['score'], 3) for r in results[:3]]
                print(f"Top 3 scores: {top_scores}")
    except Exception as e:
        print(f"Error querying '{q}': {e}")
