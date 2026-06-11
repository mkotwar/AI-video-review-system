import sys
import os
import asyncio
import time
from pathlib import Path

# Add project root to path
sys.path.append(r"c:\Mukul K\vinfo1\video-search-engine")

from app.services.frame import FrameExtractionService
from app.services.status_service import JobStatusService
from app.services.video import VideoService
import threading

# Use the first video ID from the data directory
video_id = "1398ebb1-26f1-4eac-9fa9-34a7480b70e1"

def poll_status():
    print("Starting status poller...")
    last_pct = -1
    while True:
        status = JobStatusService.get(video_id)
        pct = status.get("progress_percent", 0.0)
        step = status.get("current_step", "")
        eta = status.get("estimated_time_remaining", 0.0)
        if pct != last_pct:
            print(f"PROGRESS UPDATE: {pct}% | Step: {step} | ETA: {eta}s")
            last_pct = pct
        if status.get("status") in ["complete", "failed"]:
            print(f"Final Status: {status.get('status')} | {step}")
            break
        time.sleep(1)

async def run_pipeline():
    # Initialize status
    JobStatusService.initialize(video_id)
    print("Triggering frame extraction...")
    try:
        await FrameExtractionService.extract_frames(video_id)
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    poller = threading.Thread(target=poll_status, daemon=True)
    poller.start()
    
    asyncio.run(run_pipeline())
    
    poller.join(timeout=5)
    print("Test completed.")
