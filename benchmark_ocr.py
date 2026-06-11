import asyncio
import time
import datetime
from pathlib import Path
from loguru import logger
import glob
from app.services.ocr import OCRService

# Find some existing frames
frames_dir = Path("c:/Mukul K/vinfo1/video-search-engine/data/frames")
all_frames = list(frames_dir.rglob("*.jpg"))
test_frames = all_frames[:4]  # Let's take 4 frames for the benchmark

# Redirect loguru to a file
logger.add("c:/Mukul K/vinfo1/video-search-engine/benchmark_ocr_log.txt", mode="w")

if not test_frames:
    logger.error("No frames found for benchmarking!")
    exit(1)

logger.info(f"Using {len(test_frames)} frames for OCR benchmark.")

async def extract_with_timing(path: Path, frame_idx: int):
    start_t = time.time()
    start_str = datetime.datetime.fromtimestamp(start_t).strftime('%H:%M:%S.%f')[:-3]
    logger.info(f"Frame {frame_idx} OCR Start: {start_str}")
    
    # Run the actual OCR in a thread exactly like the pipeline
    res = await asyncio.to_thread(OCRService.extract_text, path)
    
    end_t = time.time()
    end_str = datetime.datetime.fromtimestamp(end_t).strftime('%H:%M:%S.%f')[:-3]
    logger.info(f"Frame {frame_idx} OCR End:   {end_str}")
    return res

async def run_serial():
    logger.info("--- STARTING SERIAL OCR ---")
    start = time.perf_counter()
    for idx, path in enumerate(test_frames):
        await extract_with_timing(path, idx+1)
    duration = time.perf_counter() - start
    logger.info(f"--- SERIAL OCR TOTAL TIME: {duration:.2f}s ---")
    return duration

async def run_parallel():
    logger.info("--- STARTING PARALLEL OCR ---")
    start = time.perf_counter()
    
    ocr_tasks = [extract_with_timing(path, idx+1) for idx, path in enumerate(test_frames)]
    await asyncio.gather(*ocr_tasks)
    
    duration = time.perf_counter() - start
    logger.info(f"--- PARALLEL OCR TOTAL TIME: {duration:.2f}s ---")
    return duration

async def main():
    logger.info("Loading OCR Model into memory...")
    OCRService.get_reader()
    
    serial_time = await run_serial()
    parallel_time = await run_parallel()
    
    speedup = (serial_time - parallel_time) / serial_time * 100
    multiplier = serial_time / parallel_time if parallel_time > 0 else 0
    
    logger.info(f"=== BENCHMARK RESULTS ===")
    logger.info(f"Serial Time:   {serial_time:.2f}s")
    logger.info(f"Parallel Time: {parallel_time:.2f}s")
    logger.info(f"Reduction:     {speedup:.1f}%")
    logger.info(f"Speedup:       {multiplier:.2f}x")

if __name__ == "__main__":
    asyncio.run(main())
