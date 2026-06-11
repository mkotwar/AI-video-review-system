import sys
import json
from pathlib import Path

ROOT = Path(r"c:\Mukul K\vinfo1\video-search-engine")
sys.path.insert(0, str(ROOT))

from app.services.summary_service import SummaryService
from app.services.incident_engine import IncidentEngine
from app.schemas.summary import AggregatedEvent

def main():
    vid = "a48b4d08-7e3c-4aa3-a801-0756875508b8"
    events = SummaryService.load_events(vid)
    
    out = []
    out.append("1. Show every AggregatedEvent generated")
    
    for e in events:
        out.append(f"\n--- Event: {e.event_id} ---")
        out.append(f"event_type: {e.event_type}")
        out.append(f"actor: {e.primary_object}")
        out.append(f"start_time: {e.start_time}")
        out.append(f"end_time: {e.end_time}")
        out.append(f"description: {e.description}")
        out.append(f"behavioral_flags: {e.behavioral_flags}")
        
        # also print frame_events
        fe_types = [fe.event_type for fe in e.frame_events]
        out.append(f"frame_events types: {fe_types}")

    chains = IncidentEngine.correlate_events(events)
    
    out.append("\n\n3. Show the exact IncidentChain objects returned")
    for c in chains:
        out.append(f"\nChain: {c.incident_type}")
        out.append(f"Severity: {c.severity}")
        out.append(f"Events: {[ce.get('event_type') for ce in c.chain_events]}")

    with open("crash_audit.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    main()
