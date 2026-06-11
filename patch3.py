with open("app/services/event_aggregation.py", "r", encoding="utf-8") as f:
    content = f.read()

new_method = """
    @classmethod
    def select_primary_actor(cls, objects):
        if not objects:
            return {"primary_actor": "Subject", "actor_type": "unknown", "actor_score": 0, "obj": None}

        scored_objects = []
        for obj in objects:
            t = str(obj.get("type", "")).lower()
            st = str(obj.get("subtype", "")).lower()
            text = f"{t} {st}"
            
            score = 1
            actor_type = "background"
            
            if any(k in text for k in ["person", "pedestrian", "man", "woman", "child", "elderly", "worker", "guard", "rider", "individual"]):
                score = 100
                actor_type = "human"
            elif any(k in text for k in ["vehicle", "car", "truck", "motorcycle", "bike", "bicycle", "bus", "van", "scooter"]):
                score = 90
                actor_type = "vehicle"
            elif any(k in text for k in ["animal", "dog", "cat", "livestock", "bird"]):
                score = 80
                actor_type = "animal"
            elif any(k in text for k in ["bag", "backpack", "suitcase", "box"]):
                score = 40
                actor_type = "carryable"
            elif any(k in text for k in ["furniture", "chair", "table", "desk", "sofa", "couch"]):
                score = 20
                actor_type = "furniture"
            elif any(k in text for k in ["laptop", "monitor", "phone", "electronics"]):
                score = 15
                actor_type = "electronics"
            
            scored_objects.append({
                "obj": obj,
                "score": score,
                "actor_type": actor_type
            })
            
        # Sort by score descending.
        scored_objects.sort(key=lambda x: x["score"], reverse=True)
        top = scored_objects[0]
        
        agent_name = "Subject"
        if top["obj"]:
            t = top["obj"].get("type", "").lower()
            st = top["obj"].get("subtype", "").lower()
            if top["actor_type"] == "human":
                if "guard" in st or "officer" in st: agent_name = "Security guard"
                elif "rider" in st or "motorcyclist" in st: agent_name = "Motorcyclist"
                else: agent_name = "Person"
            elif top["actor_type"] == "vehicle":
                if any(x in t or x in st for x in ["motorcycle", "scooter", "bike"]): agent_name = "Motorcycle"
                elif "car" in st or "vehicle" in t: agent_name = "Vehicle"
                elif "truck" in st or "truck" in t: agent_name = "Truck"
                else: agent_name = "Vehicle"
            else:
                agent_name = (st or t).capitalize()

        return {
            "primary_actor": agent_name,
            "actor_type": top["actor_type"],
            "actor_score": top["score"],
            "obj": top["obj"]
        }

    @classmethod
"""

if "def select_primary_actor" not in content:
    content = content.replace("    @classmethod\n    def analyze_event(", new_method + "    def analyze_event(")

old_actor_logic = """        ignore_terms = ["floor", "wall", "road", "tile", "ground", "ceiling", "sky", "background", "gray metal", "silver/grey metal", "white security booth", "white entrance building", "gray metallic", "metal security gate", "security gate", "entrance building", "gatehouse", "metal fence", "tree", "signboard", "building", "pole"]
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
            else: agent_name = (st or t).capitalize()"""

new_actor_logic = """        actor_data = cls.select_primary_actor(merged_objects)
        primary_agent_obj = actor_data["obj"]
        agent_name = actor_data["primary_actor"]"""

content = content.replace(old_actor_logic, new_actor_logic)

with open("app/services/event_aggregation.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Patch applied successfully.")
