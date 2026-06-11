import asyncio
import time
from pathlib import Path
import json

from app.services.frame import FrameExtractionService
from app.services.video import VideoService
from app.core.config import settings

async def main():
    video_id = "05715892-0b34-4fcb-9f62-608caeaadd42"
    
    start_time = time.perf_counter()
    try:
        stats = await FrameExtractionService.extract_frames(video_id)
        
        total_time = time.perf_counter() - start_time
        
        out = {
            "Frames": stats.get('frames_sent_to_qwen', 0),
            "Total Time": total_time,
            "Success": stats.get("successful_frames", 0)
        }
        
        with open("C:/Mukul K/vinfo1/video-search-engine/benchmark_results.json", "w") as f:
            json.dump(out, f, indent=4)
        print("Done")
    except Exception as e:
        with open("C:/Mukul K/vinfo1/video-search-engine/benchmark_results.json", "w") as f:
            json.dump({"error": str(e)}, f)

if __name__ == "__main__":
    asyncio.run(main())
