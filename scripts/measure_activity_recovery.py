"""Activity Recovery Measurement Script.

Reads the actual frame metadata files from data/metadata/
and measures the before/after activity extraction rate produced
by ActivityRecoveryService.

Run from the project root:
    python scripts/measure_activity_recovery.py
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Allow running from project root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.activity_recovery import ActivityRecoveryService


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def load_frames(frames_path: Path) -> List[Dict[str, Any]]:
    with frames_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def has_activities(frame: Dict) -> bool:
    return bool(frame.get("activities", []))


# ------------------------------------------------------------------ #
# Measurement                                                          #
# ------------------------------------------------------------------ #

def measure_video(video_id: str, frames: List[Dict]) -> Dict:
    total = len(frames)
    before_with  = sum(1 for f in frames if has_activities(f))
    before_empty = total - before_with

    source_counts = {"original": 0, "attributes": 0,
                     "caption": 0, "keywords": 0, "none": 0}
    recovered_activities = {}  # frame_id -> (activities, source)

    after_with = 0
    for frame in frames:
        activities, source = ActivityRecoveryService.recover(frame)
        source_counts[source] = source_counts.get(source, 0) + 1
        if activities:
            after_with += 1
        if source != "original":
            recovered_activities[frame.get("frame_id", "?")] = (activities, source)

    newly_recovered = after_with - before_with
    still_empty = total - after_with

    return {
        "video_id": video_id,
        "total_frames": total,
        "before": {
            "with_activities": before_with,
            "empty_activities": before_empty,
            "rate_pct": round(before_with / total * 100, 1),
        },
        "after": {
            "with_activities": after_with,
            "newly_recovered": newly_recovered,
            "still_empty": still_empty,
            "rate_pct": round(after_with / total * 100, 1),
        },
        "source_breakdown": source_counts,
        "frame_details": recovered_activities,
    }


def print_report(result: Dict):
    vid = result["video_id"][:8] + "..."
    b   = result["before"]
    a   = result["after"]
    src = result["source_breakdown"]

    print(f"\n{'='*62}")
    print(f"  Video: {result['video_id']}")
    print(f"{'='*62}")
    print(f"  Total frames analyzed : {result['total_frames']}")
    print()
    print(f"  BEFORE recovery")
    print(f"    Activities present  : {b['with_activities']} frames  ({b['rate_pct']}%)")
    print(f"    Activities empty    : {b['empty_activities']} frames  ({100-b['rate_pct']}%)")
    print()
    print(f"  AFTER recovery")
    print(f"    Activities present  : {a['with_activities']} frames  ({a['rate_pct']}%)")
    print(f"    Newly recovered     : {a['newly_recovered']} frames")
    print(f"    Still empty         : {a['still_empty']} frames")
    print()
    print(f"  Recovery source breakdown")
    print(f"    Original (no recovery needed) : {src.get('original', 0)}")
    print(f"    Attributes                    : {src.get('attributes', 0)}")
    print(f"    Caption                       : {src.get('caption', 0)}")
    print(f"    Keywords                      : {src.get('keywords', 0)}")
    print(f"    No recovery possible          : {src.get('none', 0)}")
    print()

    if result["frame_details"]:
        print(f"  Frame-level recovery detail")
        for fid, (acts, source) in result["frame_details"].items():
            ts = fid.split("_f")[-1] if "_f" in fid else fid
            acts_str = ", ".join(acts) if acts else "(none)"
            print(f"    [{source:10s}]  f{ts}  →  {acts_str}")


def print_combined(results: List[Dict]):
    total_frames = sum(r["total_frames"] for r in results)
    before_with  = sum(r["before"]["with_activities"] for r in results)
    after_with   = sum(r["after"]["with_activities"] for r in results)
    recovered    = sum(r["after"]["newly_recovered"] for r in results)
    still_empty  = sum(r["after"]["still_empty"] for r in results)

    total_src = {}
    for r in results:
        for k, v in r["source_breakdown"].items():
            total_src[k] = total_src.get(k, 0) + v

    print(f"\n{'='*62}")
    print(f"  COMBINED — All Videos ({len(results)} videos, {total_frames} frames)")
    print(f"{'='*62}")
    print(f"  BEFORE  activity rate : {before_with}/{total_frames} = "
          f"{round(before_with/total_frames*100, 1)}%")
    print(f"  AFTER   activity rate : {after_with}/{total_frames} = "
          f"{round(after_with/total_frames*100, 1)}%")
    print()
    print(f"  Improvement           : +{recovered} frames recovered")
    print(f"  Remaining empty       : {still_empty} frames (genuine no-activity scenes)")
    print()
    print(f"  Recovery source breakdown (combined)")
    print(f"    Original (no recovery needed) : {total_src.get('original', 0)}")
    print(f"    Attributes                    : {total_src.get('attributes', 0)}")
    print(f"    Caption                       : {total_src.get('caption', 0)}")
    print(f"    Keywords                      : {total_src.get('keywords', 0)}")
    print(f"    No recovery possible          : {total_src.get('none', 0)}")
    print(f"{'='*62}\n")


# ------------------------------------------------------------------ #
# Main                                                                 #
# ------------------------------------------------------------------ #

def main():
    project_root = Path(__file__).parent.parent
    metadata_dir = project_root / "data" / "metadata"

    frames_files = sorted(metadata_dir.glob("*_frames.json"))

    if not frames_files:
        print(f"No *_frames.json files found in {metadata_dir}")
        sys.exit(1)

    print(f"\nActivity Recovery Measurement")
    print(f"Reading {len(frames_files)} frame file(s) from {metadata_dir}\n")

    results = []
    for fp in frames_files:
        video_id = fp.stem.replace("_frames", "")
        frames = load_frames(fp)
        result = measure_video(video_id, frames)
        results.append(result)
        print_report(result)

    if len(results) > 1:
        print_combined(results)


if __name__ == "__main__":
    main()
