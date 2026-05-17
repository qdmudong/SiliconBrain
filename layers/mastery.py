import time
from layers.teacher import TeacherInterface
from layers.graph_connector import MemgraphConnector
from layers.extractor import extract_intelligence

class MasteryEngine:
    def __init__(self):
        self.teacher = TeacherInterface()
        self.connector = MemgraphConnector()

    def get_existing_entities(self):
        """Get a set of all entity names already in the graph."""
        with self.connector.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN e.name as name")
            return {r["name"].lower() for r in result}

    def master_topic(self, seed_topic: str, depth=2, max_per_level=3):
        """Recursively learn about a topic and its sub-concepts."""
        queue = [(seed_topic, 0)]
        visited = set()
        
        print(f"--- Starting Mastery Loop for: {seed_topic} (Depth: {depth}) ---")
        
        while queue:
            topic, current_depth = queue.pop(0)
            if topic.lower() in visited or current_depth > depth:
                continue
            
            visited.add(topic.lower())
            print(f"\n[MASTERY] Level {current_depth}: Learning about '{topic}'...")
            
            # 1. Get raw explanation
            raw_text = self.teacher.ask_teacher(topic)
            
            # 2. Extract structured data
            intelligence = extract_intelligence(raw_text)
            
            # 3. Ingest into graph
            existing = self.get_existing_entities()
            new_concepts = []
            
            for triple in intelligence.get("knowledge_graph", []):
                if all(k in triple for k in ["subject", "predicate", "object"]):
                    self.connector.add_triple(triple["subject"], triple["predicate"], triple["object"])
                    
                    # Discover new concepts to learn next
                    obj = triple["object"]
                    if obj.lower() not in existing and obj.lower() not in visited:
                        new_concepts.append(obj)

            for step in intelligence.get("procedural_map", []):
                if all(k in step for k in ["current_state", "action", "next_state"]):
                    self.connector.add_procedure(step["current_state"], step["action"], 
                                            step["next_state"], step.get("required_knowledge", []))

            # 4. Queue new concepts for the next depth level
            if current_depth < depth:
                added_count = 0
                for concept in new_concepts:
                    if added_count >= max_per_level:
                        break
                    if concept.lower() not in visited:
                        queue.append((concept, current_depth + 1))
                        added_count += 1
                print(f"[MASTERY] Queued {added_count} sub-topics for level {current_depth + 1}")

            print(f"[MASTERY] Finished learning '{topic}'.")
            time.sleep(2) # Prevent API rate limits

        print(f"\n--- Mastery Loop Complete for {seed_topic} ---")
        self.connector.close()

if __name__ == "__main__":
    engine = MasteryEngine()
    # Test with a focused topic
    engine.master_topic("Architecture of Memristors", depth=1, max_per_level=2)
