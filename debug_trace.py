import json
import os
import time
import sys
import traceback
from app.services.event_aggregation import EventAggregationService

def main():
    try:
        video_id = '3a8c4b20-f45a-4334-ba0a-4824b796b750'
        frames_path = f'data/metadata/{video_id}_frames.json'
        with open(frames_path, 'r') as f:
            frames = json.load(f)
            
        first_frame = frames[0]

        out = []
        out.append('--- FRAME 1 ---')
        out.append('activities: ' + str(first_frame.get('activities', [])))
        out.append('keywords: ' + str(first_frame.get('keywords', [])))
        out.append('caption: ' + str(first_frame.get('caption', '')))
        out.append('scene_description: ' + str(first_frame.get('scene_description', '')))
        out.append('object attributes: ' + str([obj.get('attributes') for obj in first_frame.get('objects', []) if isinstance(obj, dict)]))

        out.append('\n--- EXTRACT EVENT TEXT ---')
        text = EventAggregationService.extract_event_text(first_frame)
        out.append(text)

        out.append('\n--- EVENT TYPE TRACE ---')
        # We need to see what infer_event_type gets
        # process_events creates group_unified_text and calls infer_event_type
        # Let's mock group_unified_text for the first 3 frames
        group_unified_texts = [EventAggregationService.extract_event_text(f) for f in frames[:3]]
        group_unified_text = " ".join(group_unified_texts)
        out.append(f'group_unified_text: {group_unified_text[:200]}...')
        
        # Test infer_event_type directly
        evt_type = EventAggregationService.infer_event_type(first_frame.get('objects', []), first_frame.get('activities', []), first_frame.get('scene_type', ''), group_unified_text)
        out.append(f'Result from infer_event_type: {evt_type}')

        out.append('\n--- DEPLOYMENT VERIFICATION ---')
        files_to_check = [
            f'data/metadata/{video_id}_events_v2.json',
            f'data/metadata/{video_id}_summary.json',
            f'data/events/{video_id}/evt_001.json'
        ]
        for path in files_to_check:
            if os.path.exists(path):
                out.append(f'{path} last modified: {time.ctime(os.path.getmtime(path))}')
            else:
                out.append(f'{path} not found')

        with open('trace_output.txt', 'w') as f:
            f.write('\n'.join(out))

    except Exception as e:
        with open('trace_output.txt', 'w') as f:
            f.write(traceback.format_exc())

if __name__ == '__main__':
    main()
