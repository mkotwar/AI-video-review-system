import json
from app.services.narrative_builder import NarrativeBuilderService
from app.schemas.summary import AggregatedEvent

videos = {
    "Elderly Fall Video": "a629ff6d-ae6a-4fbc-ac3d-bffe9952c8bd",
    "Theft Video": "03301eee-50a4-4a3a-b5db-11f29b339233", # Found in metadata list
    "Crash Video": "09c162d9-b006-444b-8783-89b3ed025420" # Found in metadata list
}

def main():
    for name, vid in videos.items():
        print(f"\n{'='*50}\nTesting: {name}\n{'='*50}")
        try:
            with open(f"data/metadata/{vid}_events_v2.json", 'r') as f:
                data = json.load(f)
            events = [AggregatedEvent(**e) for e in data]
            prompt = NarrativeBuilderService._format_events_for_prompt(events)
            print("--- GENERATED PROMPT ---")
            print(prompt)
            print("--- LLM RESULT ---")
            incidents = NarrativeBuilderService._call_llm_reasoner(prompt)
            if incidents:
                for i in incidents:
                    print(f"Incident Type: {i.incident_type}")
                    print(f"Description: {i.description}")
                    print(f"Severity: {i.severity}")
                    print(f"Timeline: {i.timeline}")
            else:
                print("No incidents found.")
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == '__main__':
    main()
