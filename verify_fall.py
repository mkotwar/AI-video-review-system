import asyncio
import traceback
from app.services.summary_service import SummaryService

def main():
    video_id = 'a629ff6d-ae6a-4fbc-ac3d-bffe9952c8bd'
    try:
        summary = SummaryService.generate_summary(video_id)
        with open('test_results.txt', 'w') as f:
            f.write('Incidents built by SummaryService:\n')
            for inc in summary.incidents:
                f.write(f'- {inc.incident_type}: {inc.description}\n')
                f.write(f'  Timeline:\n')
                for t in inc.timeline:
                    f.write(f'    - {t}\n')
    except Exception as e:
        with open('test_results.txt', 'w') as f:
            f.write(traceback.format_exc())

if __name__ == '__main__':
    main()
