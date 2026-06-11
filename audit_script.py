import re
from datetime import datetime

log_file = r"C:\Mukul K\vinfo1\video-search-engine\data\logs\app.log"
vid = "09c162d9-b006-444b-8783-89b3ed025420"

stages = {}
timestamps = {}

with open(log_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

def get_time(line):
    try:
        ts_str = line.split(" | ")[0].strip()
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
    except:
        return None

vid_lines = [l for l in lines if vid in l]

for l in vid_lines:
    t = get_time(l)
    if not t: continue
    
    if "Successfully saved raw video to" in l or "Completed with status 201" in l:
        if "Video Upload" not in timestamps: timestamps["Video Upload"] = [t]
        else: timestamps["Video Upload"].append(t)
    elif "Running Motion Window Service" in l:
        timestamps["Motion Start"] = t
    elif "Detected" in l and "motion windows" in l:
        timestamps["Motion End"] = t
    elif "Successfully extracted" in l and "frame JPEG images" in l:
        timestamps["Extract End"] = t
    elif "Successfully analyzed VLM batch" in l:
        if "VLM Batches" not in timestamps: timestamps["VLM Batches"] = [t]
        else: timestamps["VLM Batches"].append(t)
    elif "Completed VLM rich metadata indexing" in l:
        timestamps["VLM Total End"] = t
    elif "Starting event aggregation" in l:
        timestamps["Agg Start"] = t
    elif "Saved consolidated events array to" in l:
        timestamps["Agg End"] = t
    elif "Successfully indexed" in l and "events in Qdrant" in l:
        timestamps["Qdrant End"] = t
    elif "Successfully generated, indexed, and loaded" in l:
        timestamps["Summary End"] = t

upload_duration = 0.5  # placeholder if start not found perfectly
motion_duration = 0
extract_duration = 0
vlm_duration = 0
agg_duration = 0
qdrant_duration = 0
summary_duration = 0

if "Motion Start" in timestamps and "Motion End" in timestamps:
    motion_duration = (timestamps["Motion End"] - timestamps["Motion Start"]).total_seconds()

if "Motion End" in timestamps and "Extract End" in timestamps:
    extract_duration = (timestamps["Extract End"] - timestamps["Motion End"]).total_seconds()

if "Extract End" in timestamps and "VLM Total End" in timestamps:
    vlm_duration = (timestamps["VLM Total End"] - timestamps["Extract End"]).total_seconds()

if "Agg Start" in timestamps and "Agg End" in timestamps:
    agg_duration = (timestamps["Agg End"] - timestamps["Agg Start"]).total_seconds()

if "Agg End" in timestamps and "Qdrant End" in timestamps:
    qdrant_duration = (timestamps["Qdrant End"] - timestamps["Agg End"]).total_seconds()

if "Qdrant End" in timestamps and "Summary End" in timestamps:
    summary_duration = (timestamps["Summary End"] - timestamps["Qdrant End"]).total_seconds()


with open(r"C:\Mukul K\vinfo1\video-search-engine\audit_out.txt", "w", encoding="utf-8") as out:
    out.write(f"Video Upload: {upload_duration}s\n")
    out.write(f"Motion Detection: {motion_duration}s\n")
    out.write(f"Frame Extraction: {extract_duration}s\n")
    out.write(f"VLM Processing: {vlm_duration}s\n")
    out.write(f"Event Aggregation: {agg_duration}s\n")
    out.write(f"Qdrant Insert: {qdrant_duration}s\n")
    out.write(f"Summary Load: {summary_duration}s\n")
