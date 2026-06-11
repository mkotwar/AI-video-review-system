"""Event Aggregation Service for grouping similar consecutive frame metadata records.
"""

import json
import re
import difflib
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from app.core.config import settings
from app.core.utils import format_timestamp_human
from app.services.status_service import JobStatusService

class EventAggregationService:
    """Service to group consecutive frames into semantic events based on metadata similarity."""

    HIGH_SEVERITY_KEYWORDS = {"accident", "collision", "crash", "impact", "fire", "explosion", "intrusion", "weapon", "assault", "damaged"}

    # ------------------------------------------------------------------ #
    # Intelligence extraction helpers                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def extract_event_text(frame: Dict[str, Any]) -> str:
        """Extract and normalize all textual signals from a frame for severity detection."""
        parts = []
        parts.append(str(frame.get("caption", "") or ""))
        parts.append(str(frame.get("scene_description", "") or ""))
        parts.extend(frame.get("activities", []) or [])
        parts.extend(frame.get("keywords", []) or [])
        # OCR text
        ocr_data = frame.get("ocr") or {}
        for t in ocr_data.get("detected_text", []) or []:
            parts.append(str(t))
        # Object names + attributes
        for obj in frame.get("objects", []) or []:
            if isinstance(obj, dict):
                parts.append(str(obj.get("type", "")))
                parts.append(str(obj.get("subtype", "")))
                parts.extend(obj.get("attributes", []) or [])
        # Normalize
        return " ".join(p.lower().strip() for p in parts if p and isinstance(p, str) and p.strip())

    @staticmethod
    def _extract_real_world_time(frames: List[Dict[str, Any]]) -> Optional[str]:
        """Extract the real-world clock time from OCR-detected text overlay on CCTV footage.

        Scans the first frame's OCR data for a HH:MM:SS timestamp pattern.
        """
        for frame in frames[:3]:  # Only look at first 3 frames
            texts = frame.get("ocr", {}).get("detected_text", [])
            for text in texts:
                # Match HH:MM:SS or H:MM:SS
                m = re.search(r'\b(\d{1,2}:\d{2}:\d{2})\b', str(text))
                if m:
                    return m.group(1)
        return None

    @staticmethod
    def _build_actor_description(primary_agent: Optional[Dict[str, Any]]) -> str:
        """Build a human-readable physical description of the primary actor."""
        if not primary_agent:
            return ""
        parts = []
        color = primary_agent.get("color", "").strip()
        subtype = primary_agent.get("subtype", "").strip()
        attrs = primary_agent.get("attributes", [])
        if color and color.lower() not in ("none", "n/a", "not specified", ""):
            parts.append(color)
        if subtype:
            parts.append(subtype)
        if attrs:
            # Pick the most descriptive attribute (longest, not a generic term)
            useful_attrs = [a for a in attrs if len(a) > 8 and "visible" not in a.lower()]
            if useful_attrs:
                parts.append(useful_attrs[0])
        return ", ".join(parts) if parts else ""

    @staticmethod
    def _build_participants(merged_objects: List[Dict[str, Any]], primary_agent: Optional[Dict[str, Any]]) -> Tuple[List[str], int]:
        """Build a list of participant descriptions (non-primary actors) and a total count.

        Returns:
            Tuple of (participant_descriptions, total_entity_count)
        """
        PERSON_TYPES = {"person", "personnel", "pedestrian", "guard", "security", "rider", "driver", "passenger"}
        VEHICLE_TYPES = {"vehicle", "motorcycle", "car", "truck", "bus", "scooter", "bicycle", "bike"}

        primary_key = None
        if primary_agent:
            pa_type = primary_agent.get("type", "").lower()
            pa_sub = primary_agent.get("subtype", "").lower()
            pa_col = primary_agent.get("color", "").lower()
            primary_key = (pa_type, pa_sub, pa_col)

        participants = []
        entity_count = 0

        for obj in merged_objects:
            t = obj.get("type", "").lower()
            sub = obj.get("subtype", "").lower()
            col = obj.get("color", "").strip()
            attrs = obj.get("attributes", [])

            is_person = any(p in t or p in sub for p in PERSON_TYPES)
            is_vehicle = any(v in t or v in sub for v in VEHICLE_TYPES)

            if not is_person and not is_vehicle:
                continue

            entity_count += 1

            # Skip primary agent
            obj_key = (t, sub, col.lower())
            if obj_key == primary_key:
                continue

            # Build a concise description for this participant
            desc_parts = []
            if col and col.lower() not in ("none", "n/a", "not specified", ""):
                desc_parts.append(col)
            label = sub if sub else t
            desc_parts.append(label)

            # Add one useful attribute
            useful_attrs = [a for a in attrs if len(a) > 5]
            if useful_attrs:
                desc_parts.append(f"({useful_attrs[0]})")

            desc = " ".join(desc_parts).strip()
            if desc and desc not in participants:
                participants.append(desc)

        return participants[:6], entity_count  # Cap at 6 participants for readability

    @staticmethod
    def _compute_behavioral_flags(
        activities: List[str],
        duration_seconds: float,
        participant_count: int,
        merged_objects: List[Dict[str, Any]],
        unified_text: str = ""
    ) -> List[str]:
        """Compute behavioral pattern flags from event data."""
        flags = []
        acts_lower = unified_text.lower() if unified_text else " ".join(activities).lower()

        if duration_seconds > 60:
            flags.append("extended_presence")
        elif duration_seconds > 30:
            flags.append("prolonged_activity")

        if participant_count >= 3:
            flags.append("multi_person")
        elif participant_count == 2:
            flags.append("two_persons")

        if any(kw in acts_lower for kw in ("enter", "arriv", "coming")):
            flags.append("access_event")
        if any(kw in acts_lower for kw in ("exit", "leav", "depart")):
            flags.append("egress_event")
        if any(kw in acts_lower for kw in ("park", "station", "stop")):
            flags.append("static_vehicle")
        if "carrying" in acts_lower or "carrying object" in acts_lower:
            flags.append("carrying_object")
        if "running" in acts_lower:
            flags.append("person_running")
        if "loiter" in acts_lower:
            flags.append("loitering")
            
        if any(kw in acts_lower for kw in ["accident", "collision", "crash", "impact"]):
            flags.append("collision_impact")
        if any(kw in acts_lower for kw in ["damaged front end", "crumpled", "crushed", "smashed", "broken windshield", "damaged"]):
            flags.append("vehicle_damage")
        if any(kw in acts_lower for kw in ["fire", "explosion"]):
            flags.append("fire_explosion")
        if any(kw in acts_lower for kw in ["weapon", "gun", "knife"]):
            flags.append("weapon_present")
        if any(kw in acts_lower for kw in ["intrusion", "trespassing", "unauthorized"]):
            flags.append("intrusion_detected")
        if any(kw in acts_lower for kw in ["fall", "falling", "dropped", "collapsed", "trip"]):
            flags.append("person_fall")

        # Check for motorcycles with riders/backpacks in objects
        for obj in merged_objects:
            attrs_str = " ".join(obj.get("attributes", [])).lower()
            if "backpack" in attrs_str or "luggage" in attrs_str:
                if "carrying_object" not in flags:
                    flags.append("carrying_object")

        return flags

    @staticmethod
    def _compute_confidence(
        frame_count: int,
        activities: List[str],
        frames: List[Dict[str, Any]],
    ) -> float:
        """Compute a composite confidence score (0.0–1.0) for this event."""
        # Component 1: Frame coverage (more frames = more reliable)
        frame_score = min(1.0, frame_count / 10.0)

        # Component 2: Activity source quality
        source_scores = []
        for f in frames:
            src = f.get("activity_recovery_source")
            if src is None:  # VLM-native activity
                source_scores.append(1.0)
            elif src == "attributes":
                source_scores.append(0.85)
            elif src == "caption":
                source_scores.append(0.70)
            elif src == "keywords":
                source_scores.append(0.55)
            else:  # "none"
                source_scores.append(0.0)
        activity_score = (sum(source_scores) / len(source_scores)) if source_scores else 0.5

        # Component 3: Activity richness
        richness_score = min(1.0, len(activities) / 3.0)

        confidence = (frame_score * 0.35) + (activity_score * 0.45) + (richness_score * 0.20)
        return round(confidence, 3)

    @classmethod
    def _build_narrative_sentence(
        cls,
        agent_name: str,
        actor_description: str,
        activities: List[str],
        location_text: str,
        participants: List[str],
        real_world_time: Optional[str],
        behavioral_flags: List[str],
    ) -> str:
        """Build a single investigation-grade sentence for this event."""
        acts_lower = " ".join(activities).lower()
        time_prefix = f"At {real_world_time}, " if real_world_time else ""

        # Actor phrase
        if actor_description:
            actor_phrase = f"{agent_name} ({actor_description})"
        else:
            actor_phrase = agent_name

        # Action phrase
        if "access_event" in behavioral_flags:
            action = "entered"
        elif "egress_event" in behavioral_flags:
            action = "exited"
        elif "static_vehicle" in behavioral_flags:
            action = "was parked"
        elif "person_running" in behavioral_flags:
            action = "was running"
        elif "loitering" in behavioral_flags:
            action = "was loitering"
        elif "collision_impact" in behavioral_flags:
            action = "was involved in a collision/accident"
        elif "fire_explosion" in behavioral_flags:
            action = "was involved in a fire/explosion incident"
        elif activities:
            action = f"was observed {activities[0]}"
        else:
            action = "was present"

        # Participant phrase
        if participants:
            others = ", ".join(participants[:2])
            participant_phrase = f" Others present: {others}."
        else:
            participant_phrase = ""

        # Carrying flag
        carry_phrase = " Carrying an object/bag." if "carrying_object" in behavioral_flags else ""

        return f"{time_prefix}{actor_phrase} {action} at {location_text}.{carry_phrase}{participant_phrase}"

    @staticmethod
    def jaccard_similarity(list1: List[str], list2: List[str]) -> float:
        """Computes the Jaccard similarity coefficient between two string lists."""
        set1 = set(s.lower().strip() for s in list1 if s.strip())
        set2 = set(s.lower().strip() for s in list2 if s.strip())
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        return len(set1.intersection(set2)) / len(set1.union(set2))

    @classmethod
    def calculate_similarity(cls, frame1: Dict[str, Any], frame2: Dict[str, Any]) -> float:
        """Calculates the average similarity score between two frame metadata records."""
        # 1. Caption similarity (SequenceMatcher ratio)
        cap1 = frame1.get("caption", "") or ""
        cap2 = frame2.get("caption", "") or ""
        caption_sim = difflib.SequenceMatcher(None, cap1, cap2).ratio()

        # 2. Scene type similarity (SequenceMatcher ratio)
        scene1 = frame1.get("scene_type", "") or ""
        scene2 = frame2.get("scene_type", "") or ""
        scene_sim = difflib.SequenceMatcher(None, scene1, scene2).ratio()

        # 3. Objects similarity (Jaccard similarity on serialized objects)
        objs1 = []
        for o in frame1.get("objects", []):
            if isinstance(o, dict):
                desc = f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower()
                objs1.append(desc)
            elif isinstance(o, str):
                objs1.append(o.lower())
        
        objs2 = []
        for o in frame2.get("objects", []):
            if isinstance(o, dict):
                desc = f"{o.get('color', '')} {o.get('subtype', '')} {o.get('type', '')}".strip().lower()
                objs2.append(desc)
            elif isinstance(o, str):
                objs2.append(o.lower())
        
        objects_sim = cls.jaccard_similarity(objs1, objs2)

        # 4. Activities similarity (Jaccard similarity on activity lists)
        acts1 = frame1.get("activities", []) or []
        acts2 = frame2.get("activities", []) or []
        activities_sim = cls.jaccard_similarity(acts1, acts2)

        # Calculate average similarity score
        avg_sim = (caption_sim + scene_sim + objects_sim + activities_sim) / 4.0
        return avg_sim

    @classmethod
    def infer_event_type(cls, objects: List[Dict[str, Any]], activities: List[str], scene_type: str, unified_text: str = "") -> str:
        """Infers a descriptive event type based on objects, activities, scene type, and full textual evidence."""
        if not unified_text:
            scene_lower = scene_type.lower()
            activities_lower = " ".join(activities).lower()
            unified_text = f"{scene_lower} {activities_lower}"
            
        text = unified_text.lower()
        
        # Priority 1: Collision/Accident
        if any(kw in text for kw in ["accident", "collision", "crash", "impact", "damaged"]):
            return "collision_or_accident"
            
        # Priority 2: Fire
        if any(kw in text for kw in ["fire", "explosion"]):
            return "fire_incident"
            
        # Priority 3: Weapon
        if any(kw in text for kw in ["weapon", "gun", "knife", "assault"]):
            return "weapon_incident"
            
        # Priority 4: Intrusion
        if any(kw in text for kw in ["intrusion", "trespassing", "unauthorized", "forced entry"]):
            return "intrusion_incident"
            
        # Priority 5: Generic Critical Incident fallback
        if any(kw in text for kw in cls.HIGH_SEVERITY_KEYWORDS):
            return "critical_incident"
            
        has_vehicle = any(
            "vehicle" in str(obj.get("type", "")).lower() or 
            "car" in str(obj.get("subtype", "")).lower() or 
            "truck" in str(obj.get("subtype", "")).lower() or
            "bike" in str(obj.get("subtype", "")).lower()
            for obj in objects
        )
        has_person = any("person" in str(obj.get("type", "")).lower() or "pedestrian" in str(obj.get("subtype", "")).lower() for obj in objects)
        
        # Suspicious/Restricted
        if "restricted" in text or "unauthorized" in text or "trespass" in text:
            return "restricted_area_activity"
        if "suspicious" in text or "fight" in text or "abandoned" in text:
            return "suspicious_activity"
            
        # Vehicle Movement
        if has_vehicle:
            if "park" in text or "station" in text or "stop" in text:
                return "stationary_vehicle"
            if "enter" in text or "arriv" in text:
                return "vehicle_entry"
            if "exit" in text or "leav" in text or "depart" in text:
                return "vehicle_exit"
            if "driv" in text or "mov" in text:
                return "vehicle_movement"
                
        # Pedestrian Movement
        if has_person:
            if "cross" in text:
                return "pedestrian_crossing"
            if "enter" in text or "arriv" in text:
                return "pedestrian_entry"
            if "exit" in text or "leav" in text or "depart" in text:
                return "pedestrian_exit"
            
        has_indoor = "indoor" in text or "office" in text or "room" in text or "classroom" in text
        if has_indoor:
            return "indoor_activity"
        elif activities:
            return "activity_detected"
        else:
            return "motion_detected"

    @classmethod
    def process_events(cls, video_id: str, frames_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Groups consecutive frames into events, generates aggregated fields, and saves each event JSON.

        Args:
            video_id: The UUID4 video identifier.
            frames_metadata: List of frame metadata dicts.

        Returns:
            List[Dict[str, Any]]: List of aggregated event dictionaries.
        """
        logger.info(f"Starting event aggregation for video: {video_id} with {len(frames_metadata)} frames")
        JobStatusService.update(video_id, current_step="Aggregating semantic events...", progress_percent=85.0)
        
        if not frames_metadata:
            logger.warning(f"No frame metadata provided for event aggregation (video: {video_id})")
            return []

        # Sort frames by timestamp_seconds to ensure temporal sequence
        sorted_frames = sorted(frames_metadata, key=lambda x: x.get("timestamp_seconds", 0.0))

        # Group consecutive frames based on state tracking with 1-frame tolerance
        groups: List[List[Dict[str, Any]]] = []
        current_group: List[Dict[str, Any]] = [sorted_frames[0]]
        
        # Helper to check semantic overlap
        def has_semantic_overlap(group: List[Dict], new_frame: Dict) -> bool:
            # 1. Temporal boundary check (MAX_EVENT_DURATION_SECONDS = 10)
            first_time = float(group[0].get("timestamp_seconds", 0.0))
            current_time = float(new_frame.get("timestamp_seconds", 0.0))
            duration = current_time - first_time
            
            if duration > 10.0:
                logger.debug(f"GroupDuration={duration:.2f}s ActivityMatch=False ObjectMatch=False | Reason: max_duration_exceeded")
                return False

            def is_critical(f: Dict) -> bool:
                text = cls.extract_event_text(f)
                return any(kw in text for kw in cls.HIGH_SEVERITY_KEYWORDS)

            group_critical = any(is_critical(f) for f in group)
            new_critical = is_critical(new_frame)
            
            if new_critical and not group_critical:
                return False
                
            # 2. Activity Match (Stricter)
            # Require exact phrase match or >=2 shared non-stop words
            acts_group_exact = set()
            words_group = set()
            for f in group[-3:]:
                for a in f.get("activities", []):
                    acts_group_exact.add(a.lower().strip())
                    words_group.update(w.strip() for w in a.lower().replace('/', ' ').replace(',', ' ').split())
                    
            acts_new_exact = set()
            words_new = set()
            for a in new_frame.get("activities", []):
                acts_new_exact.add(a.lower().strip())
                words_new.update(w.strip() for w in a.lower().replace('/', ' ').replace(',', ' ').split())
            
            stop_words = {"in", "on", "at", "movement", "operation", "detected", "the", "a", "an", "is", "are"}
            words_group -= stop_words
            words_new -= stop_words
            
            word_overlap = words_group.intersection(words_new)
            activity_match = False
            
            if acts_group_exact.intersection(acts_new_exact):
                activity_match = True
            elif len(word_overlap) >= 2 or (len(word_overlap) == 1 and min(len(words_group), len(words_new)) <= 1):
                activity_match = True
                
            # 3. Object Match
            def get_core_objects(frames):
                objs = set()
                for f in frames:
                    for o in f.get("objects", []):
                        if isinstance(o, dict):
                            typ = str(o.get("type", "")).lower()
                            sub = str(o.get("subtype", "")).lower()
                            if any(x in typ for x in ["vehicle", "car", "bus", "truck", "bike"]) or any(x in sub for x in ["vehicle", "car", "bus", "truck", "bike"]):
                                objs.add("vehicle")
                            if any(x in typ for x in ["person", "pedestrian", "driver", "passenger"]) or any(x in sub for x in ["person", "pedestrian", "driver", "passenger"]):
                                objs.add("person")
                return objs
                
            objs_group = get_core_objects(group[-3:])
            objs_new = get_core_objects([new_frame])
            
            object_match = bool(objs_group and objs_new and objs_group.intersection(objs_new))
            
            logger.debug(
                f"GroupDuration={duration:.2f}s "
                f"ActivityMatch={activity_match} "
                f"ObjectMatch={object_match}"
            )
            
            return activity_match or object_match

        # Iterate with 1-frame tolerance
        i = 1
        cluster_idx = 1
        while i < len(sorted_frames):
            frame = sorted_frames[i]
            frame_id = frame.get("frame_id", f"idx_{i}")
            timestamp = frame.get("timestamp_seconds", 0.0)
            activities = frame.get("activities", [])
            
            logger.debug(f"Evaluating Frame={frame_id} | Timestamp={timestamp} | Activity={activities} | EventType={frame.get('scene_type', 'unknown')}")
            
            # Check overlap with current group
            if has_semantic_overlap(current_group, frame):
                current_group.append(frame)
                logger.debug(f"MergedInto=evt_{cluster_idx:03d} | Assignment: current group")
                i += 1
            else:
                # Tolerance check: look ahead 1 frame
                if i + 1 < len(sorted_frames):
                    next_frame = sorted_frames[i+1]
                    next_frame_id = next_frame.get("frame_id", f"idx_{i+1}")
                    logger.debug(f"Checking tolerance frame lookahead: Frame={next_frame_id}")
                    if has_semantic_overlap(current_group, next_frame):
                        # The current frame is a glitch/transition, absorb it
                        current_group.append(frame)
                        current_group.append(next_frame)
                        logger.debug(f"MergedInto=evt_{cluster_idx:03d} | Assignment: glitch absorbed with next frame")
                        i += 2
                        continue
                
                # Event breaks
                logger.debug(f"Event break detected. Creating new cluster for Frame={frame_id}")
                groups.append(current_group)
                current_group = [frame]
                cluster_idx += 1
                i += 1

        if current_group:
            groups.append(current_group)

        # Prepare the events storage directory
        video_events_dir = settings.EVENTS_DIR / video_id
        video_events_dir.mkdir(parents=True, exist_ok=True)

        events: List[Dict[str, Any]] = []

        for idx, group in enumerate(groups, 1):
            event_id = f"evt_{idx:03d}"
            first_frame = group[0]
            last_frame = group[-1]

            # Calculate times
            start_time = float(first_frame.get("timestamp_start_seconds", first_frame.get("timestamp_seconds", 0.0)))
            end_time = float(last_frame.get("timestamp_end_seconds", last_frame.get("timestamp_seconds", 0.0) + 1.0))
            duration = round(end_time - start_time, 2)

            # Most common activities list (up to 2)
            from collections import Counter
            all_acts = []
            for f in group:
                for act in f.get("activities", []):
                    all_acts.append(act)
            if all_acts:
                act_counts = Counter(all_acts)
                activities = [act for act, _ in act_counts.most_common(2)]
            else:
                activities = []

            # Merge objects uniquely
            merged_objects_dict = {}
            for f in group:
                for obj in f.get("objects", []):
                    if not isinstance(obj, dict):
                        continue
                    t = obj.get("type", "unknown")
                    st = obj.get("subtype", "")
                    col = obj.get("color", "")
                    attrs = obj.get("attributes", [])
                    
                    key = (t.lower(), st.lower(), col.lower())
                    if key not in merged_objects_dict:
                        merged_objects_dict[key] = {
                            "type": t,
                            "subtype": st,
                            "color": col,
                            "attributes": set(attrs)
                        }
                    else:
                        merged_objects_dict[key]["attributes"].update(attrs)

            merged_objects = []
            for obj in merged_objects_dict.values():
                obj["attributes"] = sorted(list(obj["attributes"]))
                merged_objects.append(obj)

            # Gather source frame IDs
            source_frames = [f.get("frame_id", "") for f in group if f.get("frame_id")]

            # Gather frame_events (incidents) from VLM metadata
            frame_events = []
            seen_incident_types = set()
            for f in group:
                for inc in f.get("events", []):
                    if not isinstance(inc, dict):
                        continue
                    inc_type = str(inc.get("event_type", "")).lower().strip()
                    if not inc_type or inc_type == "none" or inc_type in seen_incident_types:
                        continue
                    seen_incident_types.add(inc_type)
                    frame_events.append({
                        "event_type": inc.get("event_type", ""),
                        "description": inc.get("description", ""),
                        "actors": inc.get("actors", []),
                        "severity": inc.get("severity", "medium"),
                        "timestamp_hint": inc.get("timestamp_hint", "")
                    })

            # 1. Location text extraction (scoped per group — fixes location_text scope leak)
            location_texts = []
            for t in first_frame.get("ocr", {}).get("detected_text", []):
                t_clean = t.strip()
                # Skip pure dates/times and common short noise, keep meaningful words
                if not re.match(r'^[\d\-\:\s\%\/]+$', t_clean) and t_clean.lower() not in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
                    if len(t_clean) > 2:
                        location_texts.append(t_clean)

            location_text = " ".join(location_texts).strip()
            if not location_text or "Gate" not in location_text:
                location_text = "the monitored area"
            else:
                match = re.search(r'(Gate\s+\d+\s+Enterance\s+Area|Gate\s+\d+\s+Entrance\s+Area)', location_text, re.IGNORECASE)
                if match:
                    location_text = match.group(1)
            
            # 2. Identify agent (Priority: Person -> Vehicle -> Object -> Structure)
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
            event_type = cls.infer_event_type(merged_objects, activities, scene_type, group_unified_text)

            # Map event type to severity
            severity_map = {
                "collision_or_accident": 100,
                "fire_incident": 100,
                "weapon_incident": 95,
                "intrusion_incident": 90,
                "critical_incident": 80,
                "restricted_area_activity": 70,
                "suspicious_activity": 60,
                "vehicle_entry": 30,
                "vehicle_exit": 30,
                "vehicle_movement": 20,
                "stationary_vehicle": 10
            }
            event_severity = severity_map.get(event_type, 15)

            # Construct final event dictionary
            event_data = {
                "event_id": event_id,
                "video_id": video_id,
                "start_time": start_time,
                "end_time": end_time,
                "timestamp_start_seconds": start_time,
                "timestamp_end_seconds": end_time,
                "timestamp_start_human": format_timestamp_human(start_time),
                "timestamp_end_human": format_timestamp_human(end_time),
                "duration_seconds": duration,
                "frame_count": len(group),
                "objects": merged_objects,
                "activities": activities,
                "primary_object": primary_object_type,
                "color": primary_color,
                "primary_activity": activity_summary,
                "source_frames": source_frames,
                "event_type": event_type,
                "summary": summary,
                # --- Narrative Intelligence Fields ---
                "scene_context": scene_context,
                "real_world_time": real_world_time,
                "actor_description": actor_description,
                "participants": participants,
                "participant_count": participant_count,
                "behavioral_flags": behavioral_flags,
                "confidence": confidence,
                "narrative_sentence": narrative_sentence,
                "location_text": location_text,
                "event_severity": event_severity,
                "unified_text": group_unified_text,
                "frame_events": frame_events,
            }

            # Save the event to disk
            event_file_path = video_events_dir / f"{event_id}.json"
            try:
                with open(event_file_path, "w", encoding="utf-8") as ef:
                    json.dump(event_data, ef, indent=4)
                logger.debug(f"Saved event {event_id} for video {video_id} to {event_file_path}")
            except Exception as exc:
                logger.error(f"Failed to write event file {event_file_path}: {exc}")

            events.append(event_data)

        # Construct the list of events matching AggregatedEvent Pydantic schema
        consolidated_events = []
        for e in events:
            source_frames = e.get("source_frames", [])
            first_frame_id = source_frames[0] if source_frames else None
            thumbnail_path = f"/api/v1/events/{video_id}/thumbnail/{first_frame_id}" if first_frame_id else None

            consolidated_events.append({
                "event_id": e["event_id"],
                "event_type": e["event_type"],
                "description": e["summary"],  # Maps summary to description
                "start_time": e["timestamp_start_human"],
                "end_time": e["timestamp_end_human"],
                "duration_seconds": e["duration_seconds"],
                "objects": e.get("objects", []),
                "activities": e.get("activities", []),
                "primary_object": e.get("primary_object", ""),
                "location_text": e.get("location_text", "the monitored area"),
                # --- Narrative Intelligence Fields (Phase D) ---
                "scene_context": e.get("scene_context", ""),
                "real_world_time": e.get("real_world_time"),
                "actor_description": e.get("actor_description", ""),
                "participants": e.get("participants", []),
                "participant_count": e.get("participant_count", 0),
                "behavioral_flags": e.get("behavioral_flags", []),
                "confidence": e.get("confidence", 0.5),
                "narrative_sentence": e.get("narrative_sentence", e["summary"]),
                "thumbnail_path": thumbnail_path,
                "event_severity": e.get("event_severity", 15),
                "unified_text": e.get("unified_text", ""),
                "frame_events": e.get("frame_events", []),
            })

        # Save consolidated JSON array to settings.METADATA_DIR / f"{video_id}_events_v2.json"
        consolidated_path = settings.METADATA_DIR / f"{video_id}_events_v2.json"
        try:
            with open(consolidated_path, "w", encoding="utf-8") as cf:
                json.dump(consolidated_events, cf, indent=4)
            logger.info(f"Saved consolidated events array to {consolidated_path} with {len(consolidated_events)} events.")
        except Exception as exc:
            logger.error(f"Failed to write consolidated events file {consolidated_path}: {exc}")

        # Add detailed logging showing number of frames loaded, events generated, and save paths
        logger.info(
            f"Event aggregation pipeline stats for video {video_id}:\n"
            f"  - Number of frames loaded: {len(frames_metadata)}\n"
            f"  - Number of events generated: {len(events)}\n"
            f"  - Event file save location (directory): {video_events_dir}\n"
            f"  - Consolidated events file: {consolidated_path}"
        )

        if events:
            logger.info(f"Example generated event (first): {json.dumps(events[0], indent=2)}")

        JobStatusService.update(video_id, events_generated=len(consolidated_events))
        return events
