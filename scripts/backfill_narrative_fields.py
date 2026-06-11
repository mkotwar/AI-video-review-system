"""Migration script: backfill narrative intelligence fields in existing _events.json files.

Reads existing frame metadata and consolidated event files, re-enriches each event
with scene_context, real_world_time, actor_description, participants,
behavioral_flags, confidence, and narrative_sentence.

Run from project root:
    python scripts/backfill_narrative_fields.py
"""

import json
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.event_aggregation import EventAggregationService


def load_frames_for_video(video_id: str):
    frames_path = settings.METADATA_DIR / f"{video_id}_frames.json"
    if frames_path.exists():
        with open(frames_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_frames_for_time_range(frames, start_human: str, end_human: str):
    """Return frames whose timestamp falls within start_human..end_human."""
    def t2s(s):
        try:
            parts = s.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return 0
        except Exception:
            return 0

    start_s = t2s(start_human)
    end_s = t2s(end_human)

    matching = []
    for f in frames:
        ts = f.get("timestamp_seconds", f.get("timestamp_start_seconds", 0))
        if start_s <= float(ts) <= end_s:
            matching.append(f)
    return matching


def backfill_events_file(video_id: str, events_path: Path, frames):
    with open(events_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    changed = 0
    for event in events:
        # Only backfill if fields are missing
        if event.get("scene_context") is not None:
            continue

        # Find frames for this event's time range
        group = get_frames_for_time_range(
            frames,
            event.get("start_time", "00:00:00"),
            event.get("end_time", "00:00:00"),
        )
        if not group:
            # Fallback: use all frames if time range yields nothing
            group = frames

        merged_objects = event.get("objects", [])

        # Agent
        PERSON_TYPES = {"person", "personnel", "pedestrian", "guard", "security", "rider"}
        VEHICLE_TYPES = {"vehicle", "motorcycle", "car", "truck", "bus", "scooter", "bicycle", "bike"}

        people = [o for o in merged_objects if any(p in o.get("type", "").lower() or p in o.get("subtype", "").lower() for p in PERSON_TYPES)]
        vehicles = [o for o in merged_objects if any(v in o.get("type", "").lower() or v in o.get("subtype", "").lower() for v in VEHICLE_TYPES)]
        primary_agent = people[0] if people else (vehicles[0] if vehicles else None)

        activities = event.get("activities", [])

        # Determine agent name
        agent_name = event.get("primary_object", "Subject") or "Subject"

        # Scene context from first frame
        scene_context = ""
        if group:
            scene_context = group[0].get("scene_description", "") or ""

        # Real-world time from OCR
        real_world_time = EventAggregationService._extract_real_world_time(group)

        # Actor description
        actor_description = EventAggregationService._build_actor_description(primary_agent)

        # Participants
        participants, participant_count = EventAggregationService._build_participants(merged_objects, primary_agent)

        # Behavioral flags
        duration = event.get("duration_seconds", 0.0)
        behavioral_flags = EventAggregationService._compute_behavioral_flags(
            activities, duration, participant_count, merged_objects
        )

        # Confidence
        confidence = EventAggregationService._compute_confidence(len(group), activities, group)

        # Location text (preserve existing)
        location_text = event.get("location_text", "Gate 1 Entrance Area")

        # Narrative sentence
        narrative_sentence = EventAggregationService._build_narrative_sentence(
            agent_name, actor_description, activities, location_text,
            participants, real_world_time, behavioral_flags,
        )

        # Patch in place
        event["scene_context"] = scene_context
        event["real_world_time"] = real_world_time
        event["actor_description"] = actor_description
        event["participants"] = participants
        event["participant_count"] = participant_count
        event["behavioral_flags"] = behavioral_flags
        event["confidence"] = confidence
        event["narrative_sentence"] = narrative_sentence
        changed += 1

    if changed:
        with open(events_path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4)
        print(f"  ✓ Backfilled {changed} events → {events_path.name}")
    else:
        print(f"  — Already up to date: {events_path.name}")

    return changed


def main():
    print("=" * 60)
    print("Backfilling narrative intelligence fields in events JSON")
    print("=" * 60)

    total_changed = 0
    for events_path in sorted(settings.METADATA_DIR.glob("*_events.json")):
        stem = events_path.name.replace("_events.json", "")
        if stem == "mock-video-id":
            continue

        video_id = stem
        print(f"\n[{video_id[:8]}...]")
        frames = load_frames_for_video(video_id)
        if not frames:
            print(f"  ! No frames found, skipping")
            continue
        print(f"  Loaded {len(frames)} frames")
        changed = backfill_events_file(video_id, events_path, frames)
        total_changed += changed

    print(f"\n{'=' * 60}")
    print(f"Done. Total events backfilled: {total_changed}")
    print("Restart uvicorn (or it will pick up changes on next reload) to see new narratives.")


if __name__ == "__main__":
    main()
