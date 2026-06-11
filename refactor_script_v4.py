import traceback

file_path = r"c:\Mukul K\vinfo1\video-search-engine\app\services\event_aggregation.py"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    analyze_event_code = """
    @classmethod
    def analyze_event(
        cls, 
        group_frames, 
        merged_objects, 
        duration,
        first_frame
    ):
        \"\"\"Core event understanding engine.\"\"\"
        # 1. Deduplicate text
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

        # 2. Strict Event Taxonomy Rules
        event_type = "normal_activity"
        event_severity = 10
        
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
            event_severity = 20

        # 3. Actor Prioritization
        ignore_terms = ["floor", "wall", "road", "tile", "ground", "ceiling", "sky", "background", "gray metal", "silver/grey metal", "white security booth", "white entrance building", "gray metallic", "metal security gate", "security gate", "entrance building", "gatehouse", "metal fence", "tree", "signboard", "building", "pole"]
        valid_objects = [o for o in merged_objects if not any(t in f'{o.get("color","")} {o.get("subtype","")} {o.get("type","")}'.lower() for t in ignore_terms)]

        persons, vehicles, animals, objects_list, furnitures = [], [], [], [], []
        for o in valid_objects:
            text = f"{o.get('type', '')} {o.get('subtype', '')}".lower()
            if any(k in text for k in ["person", "pedestrian", "guard", "rider", "man", "woman"]): persons.append(o)
            elif any(k in text for k in ["vehicle", "car", "truck", "bike", "motorcycle", "scooter", "bus"]): vehicles.append(o)
            elif any(k in text for k in ["animal", "dog", "cat", "bird"]): animals.append(o)
            elif any(k in text for k in ["furniture", "chair", "table", "desk", "sofa", "couch"]): furnitures.append(o)
            else: objects_list.append(o)

        primary_agent_obj = (persons + vehicles + animals + objects_list + furnitures + [None])[0]
        
        agent_name = "Subject"
        if primary_agent_obj:
            t = primary_agent_obj.get("type", "").lower()
            st = primary_agent_obj.get("subtype", "").lower()
            if "guard" in st or "officer" in st: agent_name = "Security guard"
            elif "rider" in st or "motorcyclist" in st: agent_name = "Motorcyclist"
            elif "person" in t or "pedestrian" in st: agent_name = "Person"
            elif any(x in t or x in st for x in ["motorcycle", "scooter", "bike"]): agent_name = "Motorcycle"
            elif "car" in st or "vehicle" in t: agent_name = "Vehicle"
            else: agent_name = (st or t).capitalize()

        # 4. Intelligence Enrichment
        scene_context = first_frame.get("scene_description", "") or ""
        real_world_time = cls._extract_real_world_time(group_frames)
        actor_description = cls._build_actor_description(primary_agent_obj)
        participants, participant_count = cls._build_participants(merged_objects, primary_agent_obj)
        behavioral_flags = cls._compute_behavioral_flags(unique_activities, duration, participant_count, merged_objects, group_unified_text)
        
        # 5. Narrative Synthesis
        joined_activities = " and ".join(unique_activities) if unique_activities else ""
        summary_parts = []
        if event_type == "collision_or_accident": summary_parts.append(f"A collision or accident occurred involving {agent_name.lower()}")
        elif event_type == "fire_incident": summary_parts.append(f"A fire or explosion incident was detected")
        elif event_type == "medical_emergency": summary_parts.append(f"A medical emergency was observed involving {agent_name.lower()}")
        elif event_type == "fall_incident": summary_parts.append(f"A fall incident was detected where {agent_name.lower()} fell")
        elif event_type == "intrusion": summary_parts.append(f"An intrusion or unauthorized access was detected by {agent_name.lower()}")
        elif event_type == "loitering": summary_parts.append(f"{agent_name} was observed loitering")
        elif event_type == "vehicle_movement": summary_parts.append(f"Vehicle movement involving {agent_name.lower()} was detected")
        elif event_type == "pedestrian_activity": summary_parts.append(f"Pedestrian activity involving {agent_name.lower()} was detected")
        else:
            if unique_activities: summary_parts.append(f"{agent_name} was observed {joined_activities}")
            else: summary_parts.append(f"{agent_name} was present")
        
        event_summary = " ".join(summary_parts)

        narrative_sentence = cls._build_narrative_sentence(
            agent_name, actor_description, unique_activities, "{location_placeholder}",
            participants, real_world_time, behavioral_flags,
        )

        return {
            "event_type": event_type,
            "event_severity": event_severity,
            "primary_actor": agent_name,
            "primary_object": agent_name,
            "event_summary": event_summary,
            "group_unified_text": group_unified_text,
            "behavioral_flags": behavioral_flags,
            "scene_context": scene_context,
            "real_world_time": real_world_time,
            "narrative_sentence": narrative_sentence,
            "participants": participants,
            "actor_description": actor_description,
            "unique_activities": unique_activities
        }

"""

    process_events_idx = -1
    for i, line in enumerate(lines):
        if "    def process_events(" in line:
            process_events_idx = i
            break

    if process_events_idx != -1 and "def analyze_event(" not in "".join(lines):
        lines.insert(process_events_idx - 1, analyze_event_code)

    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if "            # 2. Identify agent (Priority" in line:
            start_idx = i
        if "            # Construct final event dictionary" in line and start_idx != -1:
            end_idx = i
            break

    if start_idx != -1 and end_idx != -1:
        replacement_text = """            event_analysis = cls.analyze_event(group, merged_objects, duration, first_frame)

            summary = event_analysis["event_summary"] + f" at {location_text}."
            if event_analysis["participants"]:
                summary += f" Other participants: {', '.join(event_analysis['participants'])}."

            narrative_sentence = event_analysis["narrative_sentence"].replace("{location_placeholder}", location_text)

            confidence = cls._compute_confidence(len(group), event_analysis["unique_activities"], group)
            
            event_type = event_analysis["event_type"]
            event_severity = event_analysis["event_severity"]
            group_unified_text = event_analysis["group_unified_text"]
            behavioral_flags = event_analysis["behavioral_flags"]
            agent_name = event_analysis["primary_actor"]
            actor_description = event_analysis["actor_description"]
            participants = event_analysis["participants"]
            activities = event_analysis["unique_activities"]
            primary_object_type = agent_name
            primary_color = ""
            activity_summary = activities[0] if activities else "present"

"""
        new_lines = lines[:start_idx] + [replacement_text] + lines[end_idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        with open(r"c:\Mukul K\vinfo1\video-search-engine\debug.txt", "w") as f:
            f.write("SUCCESS")
    else:
        with open(r"c:\Mukul K\vinfo1\video-search-engine\debug.txt", "w") as f:
            f.write(f"FAILED TO FIND BOUNDARIES: process_events={process_events_idx}, start={start_idx}, end={end_idx}")

except Exception as e:
    with open(r"c:\Mukul K\vinfo1\video-search-engine\debug.txt", "w") as f:
        f.write(f"EXCEPTION: {e}\n{traceback.format_exc()}")
