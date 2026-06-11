import json

def main():
    path = r"c:\Mukul K\vinfo1\video-search-engine\data\metadata\a48b4d08-7e3c-4aa3-a801-0756875508b8_events_v2.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return

    out = []
    for e in events:
        out.append(f"event_type: {e.get('event_type')}")
        out.append(f"start_time: {e.get('start_time')}")
        out.append(f"end_time: {e.get('end_time')}")
        out.append(f"flags: {e.get('behavioral_flags')}")
        
        frame_events = e.get("frame_events", [])
        fe_types = [fe.get("event_type") for fe in frame_events]
        out.append(f"frame_events types: {fe_types}")
        out.append("---")
        
    with open(r"c:\Mukul K\vinfo1\video-search-engine\pure_audit.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    main()
