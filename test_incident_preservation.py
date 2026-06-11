import json
from app.services.event_aggregation import EventAggregationService

def test_accident():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "street",
            "caption": "Cars driving normally",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "blue"}],
            "activities": ["driving"],
        },
        {
            "frame_id": "f_1",
            "timestamp_seconds": 2.0,
            "scene_type": "street",
            "caption": "A car crashes into another",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "red"}],
            "activities": ["collision", "crash"],
        },
        {
            "frame_id": "f_2",
            "timestamp_seconds": 3.0,
            "scene_type": "street",
            "caption": "Cars driving normally",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "white"}],
            "activities": ["driving"],
        }
    ]
    events = EventAggregationService.process_events("test_accident", frames)
    # The critical frame should break off and form its own locked event
    critical_event = next(e for e in events if e["event_type"] == "collision_or_accident")
    assert critical_event["event_severity"] >= 90, f"Severity too low: {critical_event['event_severity']}"
    print("Accident Video: Passed")

def test_fall():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "hallway",
            "caption": "Person walking",
            "objects": [{"type": "person"}],
            "activities": ["walking"],
        },
        {
            "frame_id": "f_1",
            "timestamp_seconds": 2.0,
            "scene_type": "hallway",
            "caption": "Person slipped and fell to the floor",
            "objects": [{"type": "person"}],
            "activities": ["falling"],
        }
    ]
    events = EventAggregationService.process_events("test_fall", frames)
    critical_event = next(e for e in events if e["event_type"] == "fall_incident")
    assert critical_event["event_severity"] >= 90, f"Severity too low: {critical_event['event_severity']}"
    print("Fall Video: Passed")

def test_fire():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "room",
            "caption": "Room looks normal",
            "objects": [{"type": "furniture"}],
            "activities": [],
        },
        {
            "frame_id": "f_1",
            "timestamp_seconds": 2.0,
            "scene_type": "room",
            "caption": "Flames and smoke detected",
            "objects": [{"type": "furniture"}],
            "activities": ["fire", "burning"],
        }
    ]
    events = EventAggregationService.process_events("test_fire", frames)
    critical_event = next(e for e in events if e["event_type"] == "fire_incident")
    assert critical_event["event_severity"] >= 95, f"Severity too low: {critical_event['event_severity']}"
    print("Fire Video: Passed")

def test_traffic():
    frames = [
        {
            "frame_id": "f_0",
            "timestamp_seconds": 1.0,
            "scene_type": "street",
            "caption": "Cars driving normally",
            "objects": [{"type": "vehicle", "subtype": "car"}],
            "activities": ["driving", "moving"],
        }
    ]
    events = EventAggregationService.process_events("test_traffic", frames)
    evt = events[0]
    assert evt["event_type"] == "vehicle_movement", f"Expected vehicle_movement, got {evt['event_type']}"
    assert evt["event_severity"] < 50, f"Severity too high: {evt['event_severity']}"
    print("Normal Traffic Video: Passed")

if __name__ == "__main__":
    test_accident()
    test_fall()
    test_fire()
    test_traffic()
    print("All validation tests passed successfully!")
