import sys
import traceback

sys.path.insert(0, r"c:\Mukul K\vinfo1\video-search-engine")

try:
    from app.services.summary_service import SummaryService
    print("Imported SummaryService successfully.")
    
    vid = "a48b4d08-7e3c-4aa3-a801-0756875508b8"
    print(f"Generating summary for {vid}...")
    summary = SummaryService.generate_summary(vid)
    print("Summary generated successfully!")
    print(summary.status)
except Exception as e:
    print("CRASH DETECTED!")
    print(f"Exception Type: {type(e).__name__}")
    traceback.print_exc()
