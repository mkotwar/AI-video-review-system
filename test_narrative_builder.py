import json
from app.services.event_aggregation import EventAggregationService

def test_fall():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "indoor kitchen",
            "scene_description": "indoor kitchen",
            "caption": "Person walking",
            "objects": [{"type": "person"}],
            "activities": ["walking"],
        },
        {
            "frame_id": "f_1",
            "timestamp_seconds": 2.0,
            "scene_type": "indoor kitchen",
            "scene_description": "indoor kitchen",
            "caption": "Person slipped and fell to the floor",
            "objects": [{"type": "person"}],
            "activities": ["falling"],
        }
    ]
    events = EventAggregationService.process_events("test_fall", frames)
    narrative = events[0]["narrative_sentence"]
    print("Fall Narrative:", narrative)
    assert "walking" in narrative.lower() or "moving" in narrative.lower(), "Missing movement"
    assert "fall" in narrative.lower(), "Missing fall"
    assert "remained on the ground" in narrative.lower(), "Missing remain on floor"
    assert "indoor kitchen" in narrative.lower(), "Missing scene context"

def test_accident():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "road",
            "scene_description": "road",
            "caption": "A car crashes into another",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "red"}],
            "activities": ["collision", "crash"],
        }
    ]
    events = EventAggregationService.process_events("test_accident", frames)
    narrative = events[0]["narrative_sentence"]
    print("Accident Narrative:", narrative)
    assert "collision" in narrative.lower(), "Missing collision"
    assert "vehicle" in narrative.lower(), "Missing vehicle"
    assert "damage" in narrative.lower(), "Missing damage"

def test_office():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "office environment",
            "scene_description": "office environment",
            "caption": "Employee walking around",
            "objects": [{"type": "person", "subtype": "employee"}],
            "activities": ["working", "walking"],
        }
    ]
    events = EventAggregationService.process_events("test_office", frames)
    narrative = events[0]["narrative_sentence"]
    print("Office Narrative:", narrative)
    assert "office" in narrative.lower(), "Missing office context"
    assert "employee" in narrative.lower() or "individual" in narrative.lower(), "Missing employee/individual"
    assert "working" in narrative.lower() and "walking" in narrative.lower(), "Missing activities"

def test_traffic():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "street",
            "scene_description": "street",
            "caption": "Cars driving normally",
            "objects": [{"type": "vehicle", "subtype": "car"}],
            "activities": ["driving"],
        }
    ]
    events = EventAggregationService.process_events("test_traffic", frames)
    narrative = events[0]["narrative_sentence"]
    print("Traffic Narrative:", narrative)
    assert "vehicle" in narrative.lower(), "Missing vehicle"
    assert "moving" in narrative.lower() or "driving" in narrative.lower(), "Missing movement"

if __name__ == "__main__":
    test_fall()
    test_accident()
    test_office()
    test_traffic()
    print("All validation tests passed successfully!")
