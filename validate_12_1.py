import json
from app.services.summary_service import SummaryService

videos = {
    "Elderly Fall Video": "a629ff6d-ae6a-4fbc-ac3d-bffe9952c8bd",
    "Theft Video": "03301eee-50a4-4a3a-b5db-11f29b339233",
    "Crash Video": "09c162d9-b006-444b-8783-89b3ed025420"
}

def main():
    print("Testing Phase 12.1: Investigation Narrative Report Generator\n")
    for name, vid in videos.items():
        print(f"{'='*50}\nTesting: {name} (ID: {vid})\n{'='*50}")
        try:
            summary = SummaryService.generate_summary(vid)
            
            print(f"--- Legacy Overview ---")
            print(f"{summary.overview}\n")
            
            print(f"--- NEW Executive Summary ---")
            print(f"{summary.executive_summary}\n")
            
            print(f"--- NEW Chronological Narrative ---")
            print(f"{summary.incident_narrative}\n")
            
            print(f"--- NEW Key Findings ---")
            for k in summary.key_findings:
                print(f"  - {k}")
            print()
            
            print(f"--- NEW Recommendations ---")
            for r in summary.recommendations:
                print(f"  - {r}")
            print("\n")
            
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == '__main__':
    main()
