import asyncio
import logging
import sys
from app.services.search_service import SearchService

logging.basicConfig(level=logging.INFO)

async def test():
    with open("test_results.txt", "w") as f:
        f.write("Starting test...\n")
        try:
            SearchService.auto_index_existing_events()
            f.write("Auto-index complete.\n")
            
            results = SearchService.search_events(query="test", limit=5)
            f.write(f"Search results (no video_ids filter): {results}\n")

            results2 = SearchService.search_events(query="test", limit=5, video_ids=["mock-video-id"])
            f.write(f"Search results (with video_ids filter): {results2}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(test())
