import json
from app.services.event_aggregation import EventAggregationService

def test_engine():
    try:
        # Mock data mimicking the kitchen fall
        frames = [
            {
                "frame_id": "f1",
                "timestamp_seconds": 1.0,
                "scene_type": "indoor kitchen",
                "scene_description": "An elderly man walking in the kitchen.",
                "objects": [
                    {"type": "environment", "subtype": "floor tile", "color": "white", "attributes": ["slippery"]},
                    {"type": "person", "subtype": "elderly person", "color": "blue", "attributes": ["walking"]}
                ],
                "activities": ["walking"],
                "events": []
            },
            {
                "frame_id": "f2",
                "timestamp_seconds": 2.0,
                "scene_type": "indoor kitchen",
                "objects": [
                    {"type": "environment", "subtype": "floor tile", "color": "white"},
                    {"type": "person", "subtype": "elderly person", "color": "blue", "attributes": ["slipping"]}
                ],
                "activities": ["slipping", "lost balance"],
                "events": []
            },
            {
                "frame_id": "f3",
                "timestamp_seconds": 3.0,
                "scene_type": "indoor kitchen",
                "objects": [
                    {"type": "environment", "subtype": "floor tile", "color": "white"},
                    {"type": "person", "subtype": "elderly person", "color": "blue", "attributes": ["on floor"]}
                ],
                "activities": ["falling", "collapsed"],
                "events": []
            },
            {
                "frame_id": "f4",
                "timestamp_seconds": 4.0,
                "scene_type": "indoor kitchen",
                "objects": [
                    {"type": "environment", "subtype": "floor tile", "color": "white"},
                    {"type": "person", "subtype": "elderly person", "color": "blue", "attributes": ["motionless"]}
                ],
                "activities": ["remains on floor"],
                "events": []
            }
        ]
        
        events = EventAggregationService.process_events("vid1", frames)
        with open("c:/Mukul K/vinfo1/video-search-engine/test_out.json", "w") as f:
            json.dump(events, f, indent=2)
        with open("c:/Mukul K/vinfo1/video-search-engine/test_success.txt", "w") as f:
            f.write("Success")
    except Exception as e:
        with open("c:/Mukul K/vinfo1/video-search-engine/test_error.txt", "w") as f:
            import traceback
            f.write(traceback.format_exc())

if __name__ == "__main__":
    test_engine()
