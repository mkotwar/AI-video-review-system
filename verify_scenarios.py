import sys
import os
import io
import contextlib
from typing import List
from pydantic import BaseModel

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.schemas.summary import AggregatedEvent
from app.services.narrative_builder import NarrativeBuilderService
from app.core.config import settings

def print_header(text, f):
    f.write(f"\n{'='*50}\n{text}\n{'='*50}\n")

def run_tests():
    with open(r"c:\Mukul K\vinfo1\video-search-engine\verify_native_out.txt", "w") as f:
        events = [
        AggregatedEvent(
            start_time="00:00", end_time="00:10", event_type="person",
            description="Test event", real_world_time=None, behavioral_flags=[]
        )
    ]

        print_header("Scenario A: google-genai NOT installed", f)
        # Simulate missing module
        original_gemini_available = NarrativeBuilderService.gemini_available
        NarrativeBuilderService.gemini_available = classmethod(lambda cls: False)
        settings.GEMINI_API_KEY = "mock_key_present_but_module_missing"
        
        try:
            res = NarrativeBuilderService.generate_narrative_from_events(events)
            f.write(f"PASS: No crash. Fallback executed. Result length: {len(res)}\n")
        except Exception as e:
            f.write(f"FAIL: Crashed with: {e}\n")

        print_header("Scenario B: google-genai installed, API key missing", f)
        NarrativeBuilderService.gemini_available = original_gemini_available # Restore
        settings.GEMINI_API_KEY = "" # Empty key
        try:
            res = NarrativeBuilderService.generate_narrative_from_events(events)
            f.write(f"PASS: No crash. Fallback executed. Result length: {len(res)}\n")
        except Exception as e:
            f.write(f"FAIL: Crashed with: {e}\n")

        print_header("Scenario C: google-genai installed, invalid API key", f)
        settings.GEMINI_API_KEY = "invalid_key_xyz"
        # We simulate gemini installed by mocking gemini_available
        NarrativeBuilderService.gemini_available = classmethod(lambda cls: True)
        
        original_call = NarrativeBuilderService._call_llm_reasoner
        NarrativeBuilderService._call_llm_reasoner = classmethod(lambda cls, txt: None)
        try:
            res = NarrativeBuilderService.generate_narrative_from_events(events)
            f.write(f"PASS: No crash. Fallback executed. Result length: {len(res)}\n")
        except Exception as e:
            f.write(f"FAIL: Crashed with: {e}\n")

        print_header("Scenario D: google-genai installed, valid API key", f)
        from app.services.narrative_builder import IncidentAnalysis
        NarrativeBuilderService._call_llm_reasoner = classmethod(lambda cls, txt: [
            IncidentAnalysis(
                primary_incident="Success Test Incident",
                severity="MEDIUM",
                description="Simulated successful reasoning",
                causal_chain=["A", "B"],
                recommendations=["Action"]
            )
        ])
        try:
            res = NarrativeBuilderService.generate_narrative_from_events(events)
            f.write(f"PASS: Gemini path executed successfully. Incident Type: {res[0].incident_type}\n")
        except Exception as e:
            f.write(f"FAIL: Crashed with: {e}\n")

if __name__ == "__main__":
    run_tests()
