import sys
import traceback

with open(r"c:\Mukul K\vinfo1\video-search-engine\real_crash_dump.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    try:
        sys.path.insert(0, r"c:\Mukul K\vinfo1\video-search-engine")
        from app.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # We will use the theft video ID from the prompt!
        vid = "a48b4d08-7e3c-4aa3-a801-0756875508b8"
        response = client.get(f"/api/v1/videos/{vid}/summary")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print("EXCEPTION DETECTED!")
        traceback.print_exc(file=f)
