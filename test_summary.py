import sys
import traceback
from loguru import logger

try:
    from app.services.summary_service import SummaryService
    video_id = "3a8c4b20-f45a-4334-ba0a-4824b796b750"
    res = SummaryService.generate_summary(video_id)
    print("SUCCESS")
    print(res.overview)
except Exception as e:
    print("FAILED")
    traceback.print_exc()
