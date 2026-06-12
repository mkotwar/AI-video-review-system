import json
import traceback
import sys
import os

sys.path.insert(0, "c:/Mukul K/vinfo1/video-search-engine")

try:
    from app.services.event_aggregation import EventAggregationService
    from app.core.config import settings

    with open("c:/Mukul K/vinfo1/video-search-engine/out_val.txt", "w", encoding="utf-8") as out_f:
        out_f.write(f"MAX_EVENT_DURATION_SECONDS={settings.MAX_EVENT_DURATION_SECONDS}\n")
        out_f.write(f"EVENT_CONTINUITY_THRESHOLD={settings.EVENT_CONTINUITY_THRESHOLD}\n")
        
        frames = json.load(open("c:/Mukul K/vinfo1/video-search-engine/data/metadata/a48b4d08-7e3c-4aa3-a801-0756875508b8_frames.json", encoding="utf-8"))
        out_f.write(f"Loaded {len(frames)} frames for crash video.\n")
        
        events = EventAggregationService.process_events("a48b4d08-7e3c-4aa3-a801-0756875508b8", frames)
        out_f.write(f"Generated {len(events)} events.\n")
        
        for i, e in enumerate(events):
            out_f.write(f"Event {i}: {e['event_type']} | Duration={e['duration_seconds']}s | Start={e['start_time']} End={e['end_time']}\n")
            
        with open("c:/Mukul K/vinfo1/video-search-engine/crash_video_events.json", "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4)
            
        # Also test the SummaryService/NarrativeBuilder
        out_f.write("\nTesting SummaryService / NarrativeBuilder...\n")
        from app.services.summary_service import SummaryService
        
        # We need to pass the actual ID used by SummaryService internally which relies on the saved file
        # But for test purposes, we'll just run _collect_all_incidents directly
        from app.schemas.summary import AggregatedEvent
        agg_events = []
        for e in events:
            # Map the float start/end time to the human string for Pydantic validation
            e_copy = e.copy()
            e_copy["start_time"] = e.get("timestamp_start_human", "00:00:00")
            e_copy["end_time"] = e.get("timestamp_end_human", "00:00:00")
            agg_events.append(AggregatedEvent(**e_copy))
            
        incidents = SummaryService._collect_all_incidents(agg_events)
        
        out_f.write(f"Generated {len(incidents)} macro-incidents via NarrativeBuilder/IncidentEngine.\n")
        for i, inc in enumerate(incidents):
            out_f.write(f"Incident {i}: {inc.incident_type} (Sev: {inc.severity}) | {inc.description}\n")
            if inc.timeline:
                out_f.write("  Timeline:\n")
                for t in inc.timeline:
                    out_f.write(f"    - {t}\n")
            
except Exception as e:
    with open("c:/Mukul K/vinfo1/video-search-engine/out_val.txt", "w", encoding="utf-8") as out_f:
        out_f.write("ERROR:\n")
        out_f.write(traceback.format_exc())
