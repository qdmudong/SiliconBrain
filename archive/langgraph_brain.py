import operator
from typing import Annotated, List, TypedDict, Union
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from layers.graph_connector import MemgraphConnector

from config import get_llm_settings

# 1. Define the State
class AgentState(TypedDict):
    current_state: str
    user_input: str
    history: List[str]
    graph_results: List[str]
    next_action: str

# 2. Define the Nodes (Skills)
class HybridBrainGraph:
    def __init__(self):
        settings = get_llm_settings()
        self.llm = ChatOpenAI(
            model=settings["model"],
            base_url=f"{settings['base_url']}/v1" if "deepseek" in settings["base_url"] else settings["base_url"],
            api_key=settings["api_key"]
        )
        self.connector = MemgraphConnector()

    def router(self, state: AgentState):
        """Analyze the current state and decide the next action."""
        print(f"\n[ROUTER] Current State: {state['current_state']}")
        
        # Query the Procedural Mind Map in Memgraph for the next transition
        with self.connector.driver.session() as session:
            query = "MATCH (cs:State {name: $current_state})-[t:TRANSITION]->(ns) RETURN t.action as action, ns.name as next_state"
            result = session.run(query, current_state=state["current_state"]).single()
            
            if result:
                # IMPORTANT: Return the value that matches the conditional edge key
                return "next_step"
            return "finish"

    def retrieve_knowledge(self, state: AgentState):
        """Query the Knowledge Graph for information relevant to the current action."""
        # We need to find the transition AGAIN here to update the state
        # In a real LangGraph, we'd use a separate node to find the transition
        with self.connector.driver.session() as session:
            query = "MATCH (cs:State {name: $current_state})-[t:TRANSITION]->(ns) RETURN t.action as action, ns.name as next_state"
            result = session.run(query, current_state=state["current_state"]).single()
            
            if result:
                action = result["action"]
                next_state = result["next_state"]
                print(f"[NODE] Executing: {action}")
                
                # Heuristic knowledge retrieval
                entities = ["Phase 1", "Phase 2", "Phase 3"]
                found_info = []
                for entity in entities:
                    if entity in action or entity in next_state:
                        results = self.connector.query_kg(entity)
                        for r in results:
                            found_info.append(f"{entity} {r['predicate']} {r['object']}")
                
                return {
                    "next_action": action,
                    "current_state": next_state,
                    "graph_results": found_info,
                    "history": state["history"] + [f"Performed: {action}"]
                }
        return state

    def final_response(self, state: AgentState):
        """Generate a final response based on all gathered information."""
        print("[NODE] All steps completed. SiliconBrain is ready.")
        return state

    def build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve_knowledge", self.retrieve_knowledge)
        workflow.add_node("final_response", self.final_response)

        workflow.set_entry_point("retrieve_knowledge")
        
        # Router determines if we continue or finish
        workflow.add_conditional_edges(
            "retrieve_knowledge",
            self.router,
            {
                "next_step": "retrieve_knowledge",
                "finish": "final_response"
            }
        )

        workflow.add_edge("final_response", END)
        return workflow.compile()

if __name__ == "__main__":
    brain = HybridBrainGraph()
    app = brain.build_graph()
    
    initial_state = {
        "current_state": "Start",
        "user_input": "Execute the project roadmap.",
        "history": [],
        "graph_results": [],
        "next_action": ""
    }
    
    print("--- SiliconBrain LangGraph Execution ---")
    for output in app.stream(initial_state):
        pass
    print("\n--- Execution Finished ---")
    brain.connector.close()
