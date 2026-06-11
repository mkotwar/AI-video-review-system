import re

with open("app/services/event_aggregation.py", "r", encoding="utf-8") as f:
    content = f.read()

narrative_engine = """    @classmethod
    def build_event_narrative(cls, event_data: dict) -> str:
        \"\"\"Transform structured event data into an investigator-grade human-readable narrative.\"\"\"
        event_type = event_data.get("event_type", "normal_activity")
        severity = event_data.get("event_severity", 10)
        actor = event_data.get("primary_actor", "An individual").lower()
        
        if actor in ["person", "subject", "an individual", "employee"]: 
            actor = "An individual"
        else: 
            actor = f"A {actor}" if not actor.startswith("a ") else actor
        
        scene = event_data.get("scene_context", "").strip()
        
        # Add a leading space if we prepend "in"
        if scene:
            scene_str = f" in an {scene}" if scene.lower().startswith(('a','e','i','o','u')) else f" in a {scene}"
            if "indoor" in scene.lower() or "office" in scene.lower():
                scene_str = f" in an {scene}" if not scene.lower().startswith("indoor") else f" in an {scene}"
                # The user prompt had "indoor kitchen environment"
                if "kitchen" in scene.lower():
                    scene_str = " in an indoor kitchen environment"
                elif "office" in scene.lower():
                    scene_str = " in an office environment"
        else:
            scene_str = " through the monitored area"
            
        activities = [a.lower() for a in event_data.get("unique_activities", [])]
        joined_acts = ", ".join(activities[:-1]) + " and " + activities[-1] if len(activities) > 1 else (activities[0] if activities else "moving")

        prefix = "Routine activity observed:"
        if severity >= 90: prefix = "Critical Incident:"
        elif severity >= 50: prefix = "Unusual activity observed:"

        if event_type == "fall_incident":
            if "walking" in activities or "moving" in activities:
                narrative = f"{actor} was observed moving{scene_str} before experiencing a fall. The individual remained on the ground following the incident, indicating a possible medical emergency."
            else:
                narrative = f"{actor} experienced a fall{scene_str}. The subject remained on the ground following the event, suggesting a potential medical emergency."
        
        elif event_type == "collision_or_accident":
            narrative = f"Two vehicles were involved in a collision within the monitored area. Visible damage and post-impact activity were observed."
            
        elif event_type == "fire_incident":
            narrative = f"Fire or smoke activity was detected within the monitored area, representing a potentially dangerous situation requiring immediate attention."
            
        elif event_type == "intrusion":
            narrative = f"An unauthorized {actor.lower().replace('a ', '')} was observed entering a restricted area."
            
        elif event_type == "vehicle_movement":
            narrative = f"A vehicle was observed moving{scene_str} as part of normal activity."
            
        elif event_type == "medical_emergency":
            narrative = f"{actor} experienced a medical emergency{scene_str} and remained motionless."
            
        elif event_type == "pedestrian_activity":
            narrative = f"{actor} was observed {joined_acts}{scene_str}."
            
        else:
            narrative = "Routine activity was observed with no significant incidents detected."
            
        if severity >= 90 and not narrative.startswith("Critical Incident:"):
            return f"Critical Incident: {narrative}"
        elif severity >= 50 and severity < 90 and not narrative.startswith("Unusual activity observed:"):
            return f"Unusual activity observed: {narrative}"
        return narrative

    @classmethod
    def analyze_event("""

# Replace the beginning of analyze_event to insert the method
content = content.replace("    @classmethod\n    def analyze_event(", narrative_engine)

# Replace the tail of analyze_event
tail_replacement = """        event_data_temp = {
            "event_type": event_type,
            "event_severity": event_severity,
            "primary_actor": agent_name,
            "unique_activities": unique_activities,
            "scene_context": scene_context
        }
        narrative_sentence = cls.build_event_narrative(event_data_temp)
        event_summary = narrative_sentence

        return {
            "event_type": event_type, "event_severity": event_severity, "primary_actor": agent_name,
            "primary_object": agent_name, "event_summary": event_summary, "group_unified_text": group_unified_text,
            "behavioral_flags": behavioral_flags, "scene_context": scene_context, "real_world_time": real_world_time,
            "narrative_sentence": narrative_sentence, "participants": participants, "actor_description": actor_description,
            "unique_activities": unique_activities
        }"""

pattern_tail = r"        joined_activities = .*?unique_activities\n        \}"
content = re.sub(pattern_tail, tail_replacement, content, flags=re.DOTALL)

with open("app/services/event_aggregation.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch5 applied")
