with open("app/services/event_aggregation.py", "r", encoding="utf-8") as f:
    content = f.read()

new_overlap_logic = """
            HIGH_SEVERITY_EVENTS = {
                "fall_incident",
                "medical_emergency",
                "collision_or_accident",
                "fire_incident",
                "intrusion",
                "weapon_incident",
                "violence",
                "suspicious_activity"
            }

            def is_critical_event(f: Dict) -> str:
                text = cls.extract_event_text(f)
                evt_type = cls.infer_event_type(f.get("objects", []), f.get("activities", []), f.get("scene_type", ""), text)
                if evt_type in HIGH_SEVERITY_EVENTS:
                    f["locked"] = True
                    f["locked_type"] = evt_type
                    return evt_type
                return None

            group_critical_types = {is_critical_event(f) for f in group if is_critical_event(f)}
            new_critical_type = is_critical_event(new_frame)
            
            # Incident Locking Mechanism
            if new_critical_type and not group_critical_types:
                return False
            if group_critical_types and not new_critical_type:
                return False
                
            if group_critical_types and new_critical_type:
                if new_critical_type not in group_critical_types:
                    return False
"""

# Replace the boundary check in has_semantic_overlap
import re
pattern = r"            def is_critical\(f: Dict\).*?if g_type != n_type:\n\s+return False"
content = re.sub(pattern, new_overlap_logic.strip(), content, flags=re.DOTALL)

new_analyze_event_start = """    @classmethod
    def analyze_event(
        cls, 
        group_frames, 
        merged_objects, 
        duration,
        first_frame
    ):
        \"\"\"Core event understanding engine.\"\"\"
        unique_captions = []
        unique_keywords = []
        unique_activities = []
        for f in group_frames:
            cap = str(f.get("caption", "")).strip()
            if cap and cap not in unique_captions:
                unique_captions.append(cap)
            for kw in f.get("keywords", []):
                if kw not in unique_keywords:
                    unique_keywords.append(kw)
            for a in f.get("activities", []):
                if a not in unique_activities:
                    unique_activities.append(a)
        unique_objects_desc = []
        for obj in merged_objects:
            desc = f"{obj.get('color', '')} {obj.get('subtype', '')} {obj.get('type', '')}".strip()
            if desc and desc not in unique_objects_desc:
                unique_objects_desc.append(desc)
        group_unified_text = " ".join(unique_captions + unique_keywords + unique_activities + unique_objects_desc).strip()
        unified_lower = group_unified_text.lower()
        
        # Incident Preservation Layer
        event_type = "normal_activity"
        event_severity = 10
        
        locked_types = [f.get("locked_type") for f in group_frames if f.get("locked")]
        if locked_types:
            # Force the event to adopt the locked critical type and high severity
            event_type = locked_types[0]
            severity_map = {
                "fire_incident": 100,
                "medical_emergency": 100,
                "collision_or_accident": 95,
                "fall_incident": 95,
                "weapon_incident": 95,
                "violence": 95,
                "intrusion": 85,
                "suspicious_activity": 80
            }
            event_severity = severity_map.get(event_type, 90)
        else:
            if any(w in unified_lower for w in ["falling", "slipped", "collapsed", "lying on floor", "lost balance", "fell"]):
                event_type = "fall_incident"
                event_severity = 95
            elif any(w in unified_lower for w in ["unconscious", "motionless", "medical", "seizure"]):
                event_type = "medical_emergency"
                event_severity = 100
            elif any(w in unified_lower for w in ["collision", "crash", "impact", "damaged vehicle", "accident"]):
                event_type = "collision_or_accident"
                event_severity = 95
            elif any(w in unified_lower for w in ["smoke", "fire", "flames", "burning"]):
                event_type = "fire_incident"
                event_severity = 100
            elif any(w in unified_lower for w in ["trespass", "unauthorized", "intrusion", "break-in"]):
                event_type = "intrusion"
                event_severity = 85
            elif any(w in unified_lower for w in ["loitering", "standing still"]):
                event_type = "loitering"
                event_severity = 60
            elif any(w in unified_lower for w in ["driving", "parking", "vehicle", "car moving", "truck"]):
                event_type = "vehicle_movement"
                event_severity = 30
            elif any(w in unified_lower for w in ["walking", "running", "person", "pedestrian"]):
                event_type = "pedestrian_activity"
                event_severity = 20"""

analyze_pattern = r"    @classmethod\n    def analyze_event\(.*?event_severity = 20"
content = re.sub(analyze_pattern, new_analyze_event_start, content, flags=re.DOTALL)

with open("app/services/event_aggregation.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch4 applied successfully.")
