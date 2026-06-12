import sys
import traceback
import os

# Ensure the app is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.summary_service import SummaryService

def verify_crash():
    video_id = "03301eee-50a4-4a3a-b5db-11f29b339233"
    print(f"Testing SummaryService.generate_summary for {video_id}...")
    try:
        response = SummaryService.generate_summary(video_id)
        print("Success! Response overview length:", len(response.overview))
    except Exception as e:
        print("\n--- CRASH DETECTED ---")
        traceback.print_exc()

if __name__ == "__main__":
    verify_crash()
