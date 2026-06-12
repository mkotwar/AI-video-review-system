from app.services.narrative_builder import NarrativeBuilderService
from app.schemas.summary import AggregatedEvent

def main():
    print("Testing Semantic Narrative Mode...")
    
    events = [
        AggregatedEvent(
            start_time="00:00:03",
            end_time="00:00:08",
            actor_description="Adult male, red/black plaid shirt, blue jeans",
            activities=["losing balance", "fall", "person walking away from the camera"],
            scene_context="A kitchen interior featuring wooden cabinets",
            behavioral_flags=["collision_impact", "person_fall"],
            narrative_sentence="Adult male falls while holding an object on the kitchen floor."
        )
    ]
    
    prompt = NarrativeBuilderService._format_events_for_prompt(events)
    print("\n--- GENERATED SEMANTIC PROMPT ---")
    print(prompt)
    print("---------------------------------\n")
    
    incidents = NarrativeBuilderService._call_llm_reasoner(prompt)
    
    print("\n--- LLM REASONER RESULTS ---")
    if not incidents:
        print("No incidents found or error occurred.")
    else:
        for inc in incidents:
            print(f"Incident Type: {inc.incident_type}")
            print(f"Description: {inc.description}")
            print(f"Severity: {inc.severity}")
            print(f"Timeline: {inc.timeline}")

if __name__ == '__main__':
    main()
