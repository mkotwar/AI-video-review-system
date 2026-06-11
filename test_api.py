import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/search"
data = json.dumps({"query": "security personnel", "limit": 2}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        with open("search_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
except Exception as e:
    with open("search_test_result.json", "w") as f:
        f.write(f"ERROR: {e}")
