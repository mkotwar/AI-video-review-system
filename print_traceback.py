import sys
import traceback
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def main():
    try:
        response = client.get("/api/v1/videos/03301eee-50a4-4a3a-b5db-11f29b339233/summary")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"EXCEPTION DETECTED!")
        print(type(e).__name__)
        traceback.print_exc()

if __name__ == "__main__":
    main()
