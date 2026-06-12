import sys
import traceback
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def run_test():
    video_id = "03301eee-50a4-4a3a-b5db-11f29b339233"
    try:
        response = client.get(f"/api/v1/videos/{video_id}/summary")
        with open("crash_result3.txt", "w") as f:
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")
    except Exception as e:
        with open("crash_result3.txt", "w") as f:
            f.write(f"Exception Type: {type(e).__name__}\n")
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    run_test()
