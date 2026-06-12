import json
import os
import glob
from app.services.summary_service import SummaryService

categories = {
    "Theft / Shoplifting": ["theft", "steal", "bag", "shoplift", "take"],
    "Vehicle Collision": ["collision", "crash", "car", "vehicle", "accident"],
    "Fall / Medical": ["fall", "slip", "ground", "medical", "collapse"],
    "Fire / Smoke": ["fire", "smoke", "burn", "flame", "blaze"],
    "Physical Altercation": ["fight", "punch", "assault", "struggle", "altercation"],
    "Abandoned Object": ["abandoned", "left behind", "package", "suspicious object"],
    "Loitering": ["loitering", "standing around", "suspicious presence", "pacing"],
    "Industrial Accident": ["workplace", "forklift", "industrial", "machinery", "hard hat"],
    "Police Intervention": ["police", "officer", "arrest", "handcuffs", "cop"],
    "Normal Activity": ["walking", "browsing", "normal", "routine", "routine activity"]
}

def load_events(video_id):
    path = f"data/metadata/{video_id}_events_v2.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def find_best_videos():
    print("Scanning videos to map categories...")
    files = glob.glob("data/metadata/*_events_v2.json")
    
    category_map = {k: None for k in categories.keys()}
    
    for f in files:
        vid = os.path.basename(f).replace("_events_v2.json", "")
        events = load_events(vid)
        if not events:
            continue
            
        text_corpus = " ".join([
            str(e.get("narrative_sentence", "")) + " " + 
            " ".join(e.get("activities", [])) + " " +
            e.get("scene_context", "")
            for e in events
        ]).lower()
        
        for cat, keywords in categories.items():
            if category_map[cat] is None:
                for kw in keywords:
                    if kw in text_corpus:
                        category_map[cat] = vid
                        break
                        
    return category_map

def run_validation():
    mapping = find_best_videos()
    print("\n--- Identified Test Videos ---")
    for cat, vid in mapping.items():
        print(f"{cat}: {vid or 'NOT FOUND'}")
        
    print("\n--- Running Generation ---")
    for cat, vid in mapping.items():
        if vid:
            print(f"\n[{cat}] (Video: {vid})")
            try:
                summary = SummaryService.generate_summary(vid)
                print(f"Executive Summary:\n{summary.executive_summary}\n")
                print(f"Key Findings:")
                for k in summary.key_findings:
                    print(f" - {k}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    run_validation()
