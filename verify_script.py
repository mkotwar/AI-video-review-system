import json

def verify():
    video_id = '3a8c4b20-f45a-4334-ba0a-4824b796b750'
    base = 'c:/Mukul K/vinfo1/video-search-engine/data'
    out = []
    
    out.append('--- STEP 4: EVENT CATALOG VERIFICATION ---')
    try:
        events = json.load(open(f'{base}/metadata/{video_id}_events_v2.json', encoding='utf-8'))
        e = events[0]
        out.append(f'event_id: {e.get("event_id")}')
        out.append(f'event_type: {e.get("event_type")}')
        out.append(f'behavioral_flags: {e.get("behavioral_flags")}')
        out.append(f'description: {e.get("description")}')
    except Exception as ex:
        out.append(f'Error reading events: {ex}')

    out.append('\n--- STEP 6: NOTABLE EVENTS VERIFICATION ---')
    try:
        summary = json.load(open(f'{base}/metadata/{video_id}_summary.json', encoding='utf-8'))
        out.append('Notable events:')
        for n in summary.get('notable_events', []):
            out.append(f"- {n.get('event_type')}: {n.get('description')} (Sev {n.get('severity')})")
        
        out.append('\n--- STEP 7: AI OVERVIEW VERIFICATION ---')
        out.append(str(summary.get('ai_overview')))
    except Exception as ex:
        out.append(f'Error reading summary: {ex}')
        
    with open('c:/Mukul K/vinfo1/video-search-engine/final_verify.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
verify()
