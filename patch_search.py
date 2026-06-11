import re

with open("app/services/search_service.py", "r", encoding="utf-8") as f:
    content = f.read()

new_logic = """            # Apply score threshold, boost, and sort
            filtered = []
            for hit in raw_results:
                normalized = cls.normalize_score(float(hit.score))
                
                # Search Boost for critical incidents
                event_type = hit.payload.get("event_type", "")
                if event_type == "fire_incident":
                    normalized += 0.75
                elif event_type in ["collision_or_accident", "fall_incident"]:
                    normalized += 0.50
                elif event_type in ["medical_emergency", "weapon_incident", "violence", "intrusion"]:
                    normalized += 0.30

                if normalized >= score_threshold:
                    filtered.append({
                        "score": normalized,
                        "event_id": hit.payload.get("event_id"),
                        "video_id": hit.payload.get("video_id"),
                        "event_type": event_type,
                        "description": hit.payload.get("description"),
                        "start_time": hit.payload.get("start_time"),
                        "end_time": hit.payload.get("end_time"),
                        "duration_seconds": hit.payload.get("duration_seconds"),
                        "objects": hit.payload.get("objects", []),
                        "activities": hit.payload.get("activities", [])
                    })

            # Sort the boosted results descending, then limit
            filtered.sort(key=lambda x: x["score"], reverse=True)
            filtered = filtered[:limit]

            logger.info(f"Semantic search query '{query}' retrieved {len(filtered)} results after threshold filtering.")
            return filtered"""

pattern = r"            # Apply score threshold and limit.*?return filtered"
content = re.sub(pattern, new_logic, content, flags=re.DOTALL)

with open("app/services/search_service.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch applied")
