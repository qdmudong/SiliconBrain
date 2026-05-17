import json
from typing import List, Dict

class SimpleGraphOrchestrator:
    def __init__(self, data_path: str):
        with open(data_path, "r") as f:
            self.data = json.load(f)
        self.kg = self.data.get("knowledge_graph", [])
        self.pm = self.data.get("procedural_map", [])

    def query_knowledge(self, subject: str, predicate: str = None) -> List[str]:
        results = []
        for triple in self.kg:
            if triple["subject"].lower() == subject.lower():
                if not predicate or triple["predicate"].lower() == predicate.lower():
                    results.append(triple["object"])
        return results

    def get_procedure_step(self, current_state: str) -> Dict:
        for step in self.pm:
            if step["current_state"].lower() == current_state.lower():
                return step
        return None

    def traverse_roadmap(self):
        print("--- SiliconBrain Roadmap Traversal ---")
        state = "Start"
        while state:
            step = self.get_procedure_step(state)
            if not step:
                print(f"Reached final state or unknown state: {state}")
                break
            
            print(f"\n[CURRENT STATE]: {state}")
            print(f"[ACTION]: {step['action']}")
            
            # Simulated "Reasoning" using the KG
            # In Phase 3, this would be the LLM querying the KG
            if "Knowledge Graph" in step['next_state']:
                tech = self.query_knowledge("Phase 1", "tech stack")
                print(f"[REASONING]: To populate the KG, I need Phase 1 tech: {tech}")
            elif "Procedural Mind Maps" in step['next_state']:
                tech = self.query_knowledge("Phase 2", "tech stack")
                print(f"[REASONING]: To define logic, I need Phase 2 tech: {tech}")
            elif "Task execution" in step['next_state']:
                tech = self.query_knowledge("Phase 3", "tech stack")
                print(f"[REASONING]: For orchestration, I need Phase 3 tech: {tech}")

            state = step['next_state']

if __name__ == "__main__":
    orchestrator = SimpleGraphOrchestrator("data/manifesto_extracted.json")
    orchestrator.traverse_roadmap()
