import json
from app.services.event_aggregation import EventAggregationService

output_file = "test_output_results.txt"

def print_events(name, events):
    with open(output_file, "a") as f:
        f.write(f"=== {name} ===\n")
        for e in events:
            f.write(f"Type: {e['event_type']}\n")
            f.write(f"Primary Actor: {e['primary_object']}\n")
            f.write(f"Severity: {e.get('event_severity', 'N/A')}\n")
            f.write(f"Summary: {e['summary']}\n")
            f.write("-" * 40 + "\n")

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
            "caption": "A red car crashes into a pedestrian",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "red"}, {"type": "person", "subtype": "pedestrian", "color": "blue"}],
            "activities": ["crash", "collision"],
        }
    ]
    events = EventAggregationService.process_events("test_accident", frames)
    print_events("Accident Video", events)

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
            "objects": [{"type": "person", "subtype": "elderly", "color": "gray"}, {"type": "furniture", "subtype": "floor"}],
            "activities": ["falling", "slipped"],
        }
    ]
    events = EventAggregationService.process_events("test_fall", frames)
    print_events("Fall Video", events)

def test_traffic():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "traffic intersection",
            "caption": "Cars driving normally",
            "objects": [{"type": "vehicle", "subtype": "car", "color": "blue"}, {"type": "vehicle", "subtype": "truck", "color": "white"}],
            "activities": ["driving", "moving"],
        }
    ]
    events = EventAggregationService.process_events("test_traffic", frames)
    print_events("Traffic Video", events)

def test_office():
    frames = [
        {
            "frame_id": "frame_0",
            "timestamp_seconds": 1.0,
            "scene_type": "office room",
            "caption": "People sitting at desks and working",
            "objects": [{"type": "person", "subtype": "employee", "color": "black"}, {"type": "furniture", "subtype": "desk"}],
            "activities": ["sitting", "working"],
        }
    ]
    events = EventAggregationService.process_events("test_office", frames)
    print_events("Office Video", events)

if __name__ == "__main__":
    with open(output_file, "w") as f:
        f.write("")
    test_accident()
    test_fall()
    test_traffic()
    test_office()
