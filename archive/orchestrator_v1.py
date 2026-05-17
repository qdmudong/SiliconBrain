from layers.graph_connector import MemgraphConnector

class GraphOrchestratorV1:
    def __init__(self):
        self.connector = MemgraphConnector()

    def query_knowledge(self, subject: str, predicate: str = None):
        results = self.connector.query_kg(subject)
        if predicate:
            return [r["object"] for r in results if r["predicate"].lower() == predicate.lower()]
        return [r["object"] for r in results]

    def get_procedure_step(self, current_state: str):
        with self.connector.driver.session() as session:
            query = "MATCH (cs:State {name: $current_state})-[t:TRANSITION]->(ns) RETURN t.action as action, ns.name as next_state"
            result = session.run(query, current_state=current_state).single()
            if result:
                return {"action": result["action"], "next_state": result["next_state"]}
        return None

    def traverse_roadmap(self):
        print("--- SiliconBrain Roadmap Traversal (Live Memgraph) ---")
        state = "Start"
        while state:
            step = self.get_procedure_step(state)
            if not step:
                print(f"Reached final state or unknown state: {state}")
                break
            
            print(f"\n[CURRENT STATE]: {state}")
            print(f"[ACTION]: {step['action']}")
            
            # Simulated "Reasoning" using the live KG
            if "Knowledge Graph" in step['next_state']:
                tech = self.query_knowledge("Phase 1", "tech stack")
                print(f"[GRAPH RETRIEVAL]: To populate the KG, I need Phase 1 tech: {tech}")
            elif "Procedural Mind Maps" in step['next_state']:
                tech = self.query_knowledge("Phase 2", "tech stack")
                print(f"[GRAPH RETRIEVAL]: To define logic, I need Phase 2 tech: {tech}")
            elif "Task execution" in step['next_state']:
                tech = self.query_knowledge("Phase 3", "tech stack")
                print(f"[GRAPH RETRIEVAL]: For orchestration, I need Phase 3 tech: {tech}")

            state = step['next_state']
        self.connector.close()

if __name__ == "__main__":
    orchestrator = GraphOrchestratorV1()
    orchestrator.traverse_roadmap()
