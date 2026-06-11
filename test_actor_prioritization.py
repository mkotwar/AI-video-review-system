import json
from app.services.event_aggregation import EventAggregationService

def test_fall():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "indoor hallway",
            "caption": "An elderly person walking",
            "objects": [{"type": "person", "subtype": "elderly", "color": "gray"}],
            "activities": ["walking"],
        },
        {
            "frame_id": "frame_1",
            "timestamp_seconds": 2.0,
            "scene_type": "indoor hallway",
            "caption": "The person slipped and is falling to the floor",
            "objects": [{"type": "person", "subtype": "elderly", "color": "gray"}, {"type": "floor tile", "subtype": "floor"}],
            "activities": ["falling", "slipped"],
        }
    ]
    events = EventAggregationService.process_events("test_fall", frames)
    actor = events[0]["primary_actor"]
    assert actor.lower() == "person", f"Expected Person, got {actor}"
    print("Fall Video: Passed")

def test_accident():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "outdoor street",
            "caption": "A red car is driving down the road",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "red"}],
            "activities": ["driving"],
        },
        {
            "frame_id": "frame_1",
            "timestamp_seconds": 2.0,
            "scene_type": "outdoor street",
            "caption": "A red car crashes on the road",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "red"}, {"type": "road", "subtype": "street", "color": "black"}],
            "activities": ["crash", "collision"],
        }
    ]
    events = EventAggregationService.process_events("test_accident", frames)
    actor = events[0]["primary_actor"]
    assert actor.lower() == "vehicle", f"Expected Vehicle, got {actor}"
    print("Accident Video: Passed")

def test_office():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "office room",
            "caption": "People sitting at desks and working",
            "objects": [{"type": "person", "subtype": "employee", "color": "black"}, {"type": "furniture", "subtype": "desk"}, {"type": "electronics", "subtype": "laptop"}],
            "activities": ["sitting", "working"],
        }
    ]
    events = EventAggregationService.process_events("test_office", frames)
    actor = events[0]["primary_actor"]
    assert actor.lower() == "person", f"Expected Person, got {actor}"
    print("Office Video: Passed")

def test_empty():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "empty room",
            "caption": "An empty room with just a floor",
            "objects": [{"type": "floor", "subtype": "tile", "color": "white"}],
            "activities": [],
        }
    ]
    events = EventAggregationService.process_events("test_empty", frames)
    actor = events[0]["primary_actor"]
    assert actor.lower() == "floor", f"Expected Background Object (Floor), got {actor}"
    print("Empty Scene Video: Passed")

if __name__ == "__main__":
    test_fall()
    test_accident()
    test_office()
    test_empty()
    print("All validation tests passed successfully!")
