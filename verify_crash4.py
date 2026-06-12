import sys
import traceback
import os

sys.path.insert(0, r"c:\Mukul K\vinfo1\video-search-engine")

def verify_crash():
    try:
        from app.services.summary_service import SummaryService
        video_id = "03301eee-50a4-4a3a-b5db-11f29b339233"
        response = SummaryService.generate_summary(video_id)
        with open(r"c:\Mukul K\vinfo1\video-search-engine\real_crash.txt", "w") as f:
            f.write("Success! Response overview length: " + str(len(response.overview)))
    except Exception as e:
        with open(r"c:\Mukul K\vinfo1\video-search-engine\real_crash.txt", "w") as f:
            f.write(f"Exception Type: {type(e).__name__}\n")
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    verify_crash()
