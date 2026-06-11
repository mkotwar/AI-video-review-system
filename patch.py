import os

file_path = "c:/Mukul K/vinfo1/video-search-engine/app/services/event_aggregation.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Chunk 1
content = content.replace(
    'HIGH_SEVERITY_KEYWORDS = {"accident", "collision", "crash", "impact", "fire", "explosion", "intrusion", "weapon", "assault", "damaged"}',
    'HIGH_SEVERITY_KEYWORDS = {"accident", "collision", "crash", "impact", "fire", "explosion", "intrusion", "weapon", "assault", "damaged", "slip", "fall", "collapse", "medical", "emergency"}'
)

# Chunk 2
old_flags = """        if any(kw in acts_lower for kw in ["fall", "falling", "dropped", "collapsed", "trip"]):
            flags.append("person_fall")"""
new_flags = """        if any(kw in acts_lower for kw in ["fall", "falling", "dropped", "collapsed", "trip", "slip", "stumble", "lost balance"]):
            flags.append("person_fall")

        if "person_fall" in flags and (duration_seconds >= 2.0 or any(kw in acts_lower for kw in ["remains on floor", "motionless", "unconscious"])):
            flags.append("prolonged_ground_presence")
            flags.append("medical_attention_required")"""
content = content.replace(old_flags, new_flags)

# Chunk 3
old_infer = """    @classmethod
    def infer_event_type(cls, objects: List[Dict[str, Any]], activities: List[str], scene_type: str, unified_text: str = "") -> str:
        \"\"\"Infers a descriptive event type based on objects, activities, scene type, and full textual evidence.\"\"\"
        if not unified_text:
            scene_lower = scene_type.lower()
            activities_lower = " ".join(activities).lower()
            unified_text = f"{scene_lower} {activities_lower}"
            
        text = unified_text.lower()
        
        # Priority 1: Collision/Accident
        if any(kw in text for kw in ["accident", "collision", "crash", "impact", "damaged"]):
            return "collision_or_accident" """
            
new_infer = """    @classmethod
    def infer_event_type(cls, objects: List[Dict[str, Any]], activities: List[str], scene_type: str, unified_text: str = "", behavioral_flags: List[str] = None) -> str:
        \"\"\"Infers a descriptive event type based on objects, activities, scene type, and full textual evidence.\"\"\"
        if behavioral_flags is None:
            behavioral_flags = []
            
        if not unified_text:
            scene_lower = scene_type.lower()
            activities_lower = " ".join(activities).lower()
            unified_text = f"{scene_lower} {activities_lower}"
            
        text = unified_text.lower()
        
        # Priority 1: Medical Emergency
        if "medical_attention_required" in behavioral_flags or any(kw in text for kw in ["medical emergency"]):
            return "medical_emergency"
            
        # Priority 2: Fall Incident
        if "person_fall" in behavioral_flags or any(kw in text for kw in ["slip and fall", "falling down"]):
            return "fall_incident"
        
        # Priority 3: Collision/Accident
        if any(kw in text for kw in ["accident", "collision", "crash", "impact", "damaged"]):
            return "collision_or_accident" """
content = content.replace(old_infer, new_infer)

# Chunk 4
old_map = """            # Map event type to severity
            severity_map = {
                "collision_or_accident": 100,"""
new_map = """            # Map event type to severity
            severity_map = {
                "medical_emergency": 100,
                "fall_incident": 85,
                "collision_or_accident": 80,"""
content = content.replace(old_map, new_map)

# Chunk 5 & 6
old_agent = """            # 2. Identify agent (Priority: Person -> Vehicle -> Object -> Structure)
            ignore_terms = ["gray metal", "silver/grey metal", "white security booth", "carrying bag", "backpack", "duffel", "white entrance building", "gray metallic", "metal security gate", "security gate", "entrance building", "gatehouse", "metal fence", "tree", "signboard", "building", "pole"]

            def is_valid_agent(obj_dict):
                desc = f'{obj_dict.get("color","")} {obj_dict.get("subtype","")} {obj_dict.get("type","")}'.lower()
                for term in ignore_terms:
                    if term in desc:
                        return False
                return True

            valid_objects = [o for o in merged_objects if is_valid_agent(o)]

            people = [o for o in valid_objects if "person" in o.get("type", "").lower() or "guard" in o.get("subtype", "").lower() or "rider" in o.get("subtype", "").lower() or "pedestrian" in o.get("subtype", "").lower()]
            vehicles = [o for o in valid_objects if "vehicle" in o.get("type", "").lower() or "motorcycle" in o.get("type", "").lower() or "car" in o.get("subtype", "").lower() or "bike" in o.get("subtype", "").lower() or "scooter" in o.get("subtype", "").lower()]

            primary_agent = None
            if people:
                primary_agent = people[0]
            elif vehicles:
                primary_agent = vehicles[0]
            elif valid_objects:
                primary_agent = valid_objects[0]

            agent_name = "Subject"
            if primary_agent:
                t = primary_agent.get("type", "").lower()
                st = primary_agent.get("subtype", "").lower()
                if "guard" in st or "officer" in st:
                    agent_name = "Security guard"
                elif "rider" in st or "motorcyclist" in st:
                    agent_name = "Motorcyclist"
                elif "person" in t:
                    agent_name = "Person"
                elif "motorcycle" in t or "motorcycle" in st or "scooter" in st or "bike" in st:
                    agent_name = "Motorcycle"
                elif "car" in st or "vehicle" in t:
                    agent_name = "Vehicle"
                else:
                    agent_name = (st or t).capitalize()

            # --- Intelligence Enrichment (Phase A) ---
            # Scene context: carry forward VLM's scene understanding from first frame
            scene_context = first_frame.get("scene_description", "") or ""

            # Real-world time: extract from OCR overlay
            real_world_time = cls._extract_real_world_time(group)

            # Actor description: physical details of primary agent
            actor_description = cls._build_actor_description(primary_agent)

            # Participants: other persons/vehicles in the scene
            participants, participant_count = cls._build_participants(merged_objects, primary_agent)

            # Narrative sentence: one-line investigation summary for this event
            # Combine all unified texts for the group to pass to flags/event_type computation
            group_unified_texts = [cls.extract_event_text(f) for f in group]
            group_unified_text = " ".join(group_unified_texts)

            # Behavioral flags: pattern analysis
            behavioral_flags = cls._compute_behavioral_flags(activities, duration, participant_count, merged_objects, group_unified_text)

            # Confidence: composite reliability score
            confidence = cls._compute_confidence(len(group), activities, group)

            # Narrative sentence: one-line investigation summary for this event
            narrative_sentence = cls._build_narrative_sentence(
                agent_name, actor_description, activities, location_text,
                participants, real_world_time, behavioral_flags,
            )

            primary_object_type = agent_name
            primary_color = primary_agent.get("color", "") if primary_agent else ""
            activity_summary = activities[0] if activities else "present"

            # 3. Description synthesis
            joined_activities = " and ".join(activities) if activities else ""
            acts_lower = joined_activities.lower()

            if "interact" in acts_lower:
                summary = f"Security guard interacted with an arriving rider at {location_text}."
            elif agent_name == "Motorcyclist" and "carrying" in acts_lower:
                summary = f"Motorcyclist carrying a backpack or object approached {location_text}."
            elif agent_name == "Security guard":
                if "stand" in acts_lower:
                    summary = f"Security guard was observing the checkpoint at {location_text}."
                else:
                    summary = f"Security guard was present at {location_text}."
            elif agent_name == "Motorcycle":
                summary = f"Motorcycle entered or moved through {location_text}."
            else:
                if activities:
                    summary = f"{agent_name} was observed {joined_activities} at {location_text}."
                else:
                    summary = f"{agent_name} was present at {location_text}."

            # Infer event type with full taxonomy
            scene_type = first_frame.get("scene_type", "unknown")
            event_type = cls.infer_event_type(merged_objects, activities, scene_type, group_unified_text)"""

new_agent = """            # 2. Identify agent (Actor Prioritization Engine)
            def get_actor_priority(obj_dict):
                t = str(obj_dict.get("type", "")).lower()
                st = str(obj_dict.get("subtype", "")).lower()
                combined = f"{t} {st}"
                
                # Level 1: Humans
                if any(kw in combined for kw in ["person", "pedestrian", "worker", "driver", "elderly", "guard", "rider", "officer", "individual"]):
                    return 1
                # Level 2: Vehicles
                if any(kw in combined for kw in ["vehicle", "motorcycle", "bicycle", "car", "truck", "bus", "scooter", "van", "bike"]):
                    return 2
                # Level 3: Animals
                if any(kw in combined for kw in ["animal", "dog", "cat", "bird"]):
                    return 3
                # Level 4: Moveables
                if any(kw in combined for kw in ["furniture", "electronics", "bag", "luggage", "box", "chair", "table", "laptop"]):
                    return 4
                # Level 5: Environmentals (always last)
                return 5

            sorted_objects = sorted(merged_objects, key=get_actor_priority)
            primary_agent = sorted_objects[0] if sorted_objects else None

            agent_name = "Subject"
            if primary_agent:
                t = primary_agent.get("type", "").lower()
                st = primary_agent.get("subtype", "").lower()
                if "elderly" in st or "elderly" in t:
                    agent_name = "Elderly individual"
                elif "worker" in st or "worker" in t:
                    agent_name = "Worker"
                elif "guard" in st or "officer" in st:
                    agent_name = "Security guard"
                elif "rider" in st or "motorcyclist" in st:
                    agent_name = "Motorcyclist"
                elif "person" in t or "pedestrian" in st or "driver" in st or "person" in st:
                    agent_name = "Person"
                elif "motorcycle" in t or "motorcycle" in st or "scooter" in st or "bike" in st:
                    agent_name = "Motorcycle"
                elif "car" in st or "vehicle" in t:
                    agent_name = "Vehicle"
                else:
                    agent_name = (st or t).capitalize()

            # --- Intelligence Enrichment (Phase A) ---
            # Scene context: carry forward VLM's scene understanding from first frame
            scene_context = first_frame.get("scene_description", "") or ""

            # Real-world time: extract from OCR overlay
            real_world_time = cls._extract_real_world_time(group)

            # Actor description: physical details of primary agent
            actor_description = cls._build_actor_description(primary_agent)

            # Participants: other persons/vehicles in the scene
            participants, participant_count = cls._build_participants(merged_objects, primary_agent)

            # Narrative sentence: one-line investigation summary for this event
            # Combine all unified texts for the group to pass to flags/event_type computation
            group_unified_texts = [cls.extract_event_text(f) for f in group]
            group_unified_text = " ".join(group_unified_texts)

            # Behavioral flags: pattern analysis
            behavioral_flags = cls._compute_behavioral_flags(activities, duration, participant_count, merged_objects, group_unified_text)

            # Confidence: composite reliability score
            confidence = cls._compute_confidence(len(group), activities, group)

            # Narrative sentence: one-line investigation summary for this event
            narrative_sentence = cls._build_narrative_sentence(
                agent_name, actor_description, activities, location_text,
                participants, real_world_time, behavioral_flags,
            )

            primary_object_type = agent_name
            primary_color = primary_agent.get("color", "") if primary_agent else ""
            activity_summary = activities[0] if activities else "present"

            # Infer event type with full taxonomy
            scene_type = first_frame.get("scene_type", "unknown")
            event_type = cls.infer_event_type(merged_objects, activities, scene_type, group_unified_text, behavioral_flags)

            # 3. Description synthesis
            joined_activities = " and ".join(activities) if activities else ""
            acts_lower = joined_activities.lower()

            if event_type == "medical_emergency":
                summary = f"An {agent_name.lower()} was observed {joined_activities} inside {location_text}. The individual remained on the floor after the fall, indicating a possible medical emergency requiring attention."
                summary = summary.replace("An person", "A person").replace("An security", "A security").replace("An worker", "A worker").replace("An motorcyclist", "A motorcyclist").replace("An vehicle", "A vehicle")
            elif event_type == "fall_incident":
                summary = f"An {agent_name.lower()} was observed slipping and falling inside {location_text}."
                summary = summary.replace("An person", "A person").replace("An security", "A security").replace("An worker", "A worker")
            elif "interact" in acts_lower:
                summary = f"Security guard interacted with an arriving rider at {location_text}."
            elif agent_name == "Motorcyclist" and "carrying" in acts_lower:
                summary = f"Motorcyclist carrying a backpack or object approached {location_text}."
            elif agent_name == "Security guard":
                if "stand" in acts_lower:
                    summary = f"Security guard was observing the checkpoint at {location_text}."
                else:
                    summary = f"Security guard was present at {location_text}."
            elif agent_name == "Motorcycle":
                summary = f"Motorcycle entered or moved through {location_text}."
            else:
                if activities:
                    summary = f"{agent_name} was observed {joined_activities} at {location_text}."
                else:
                    summary = f"{agent_name} was present at {location_text}." """

content = content.replace(old_agent, new_agent)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully!")
