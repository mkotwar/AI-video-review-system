with open("app/services/event_aggregation.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "# 2. Identify agent (Priority:" in line:
        skip = True
        # Append the replacement code right here!
        replacement = """            event_analysis = cls.analyze_event(group, merged_objects, duration, first_frame)
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
        new_lines.append(replacement)
    elif "# Construct final event dictionary" in line and skip:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open("app/services/event_aggregation.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Replaced lines successfully.")
