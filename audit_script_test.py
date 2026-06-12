import json
import sys
from app.schemas.summary import AggregatedEvent
from app.services.summary_service import SummaryService

def main():
    try:
        with open('crash_video_events.json', 'r') as f:
            data = json.load(f)
        events = [AggregatedEvent(**e) for e in data]
        print(f"Loaded {len(events)} events.")
        
        from app.core.config import settings
        print(f"GEMINI_API_KEY: {bool(settings.GEMINI_API_KEY)}")
        
        # Test narrative builder
        from app.services.narrative_builder import NarrativeBuilderService
        chains = NarrativeBuilderService.generate_narrative_from_events(events)
        print(f"NarrativeBuilder returned {len(chains)} chains.")
        
        # Test SummaryService
        stats = SummaryService.compute_statistics(events)
        notable = SummaryService.extract_notable_events(events, 'test')
        narrative = SummaryService.build_narrative(events, stats, notable, incidents=chains)
        print(f"Narrative Output: {narrative}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
