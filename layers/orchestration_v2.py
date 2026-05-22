import json
import operator
from typing import Annotated, List, TypedDict, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from layers.graph_connector import MemgraphConnector
from config import get_llm_settings

# 1. Define the State
class AgentState(TypedDict, total=False):
    user_input: str
    current_state: str
    thought_process: List[str]
    graph_results: List[str]
    history: List[str]
    chat_history: List[dict]
    final_response: str
    efficiency_metrics: dict
    steps: int
    visited: List[str]
    cycle_detected: bool

# 2. The Phase 3 Orchestrator
class SiliconBrainPhase3:
    def __init__(self):
        # Using Centralized Config
        settings = get_llm_settings()
        self.model_name = settings["model"]
        self.provider = settings.get("api_key") == "ollama" and "LOCAL (20W)" or "EXTERNAL API"
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            base_url=f"{settings['base_url']}/v1" if "deepseek" in settings["base_url"] else settings["base_url"],
            api_key=settings["api_key"],
            temperature=0
        )
        self.connector = MemgraphConnector()
        self.total_tokens_est = 0
        self.graph_context_size = self._estimate_graph_size()

    def _estimate_graph_size(self):
        """Calculate total characters in the graph to estimate 'Full Context' tokens."""
        try:
            with self.connector.driver.session() as session:
                # Sum of all node names and relationship types
                result = session.run("MATCH (n:Entity)-[r]->(o) RETURN sum(size(n.name) + size(o.name) + size(r.type)) as total")
                size = result.single()["total"] or 0
                return size // 4 # Roughly 4 chars per token
        except:
            return 10000 # Fallback if database is busy

    def log_call(self, phase, prompt, response):
        # Simple token estimation: ~4 chars per token
        p_tokens = len(prompt) // 4
        r_tokens = len(response) // 4
        self.total_tokens_est += (p_tokens + r_tokens)
        
        print(f"\n--- LLM {phase} ({self.model_name}) ---")
        print(f"Provider: {self.provider}")
        print(f"Estimated Tokens for this call: {p_tokens + r_tokens}")
        print(f"Response: {response[:200]}...")
        print(f"--------------------------------\n")

    def interpreter(self, state: AgentState):
        """Interpret user input and map it to a starting state in the graph."""
        self.total_tokens_est = 0
        print("\n" + "="*50)
        print(f"🧠 [INTERPRETER] PHASE START (Model: {self.model_name})")
        print(f"User Input: '{state['user_input']}'")
        
        chat_history = state.get("chat_history", [])
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history])
        
        with self.connector.driver.session() as session:
            result = session.run("MATCH (s:State) RETURN s.name as name")
            available_states = [r["name"] for r in result]
        
        # Optimization: Only show a relevant subset of states if the list is huge
        print(f"Memory contains {len(available_states)} workflow states.")
        
        prompt = f"""
        Conversation History:
        {chat_history_str}
        
        User Input: {state['user_input']}
        
        Your goal is to map this input (considering the conversation history if relevant) to ONE of the available workflow states.
        Available States (Partial List): {available_states[:20]} ... (and {len(available_states)-20} more)
        
        Return ONLY the state name that best matches. If no specific match, return 'Start'.
        """
        
        raw_response = self.llm.invoke([HumanMessage(content=prompt)])
        response = raw_response.content.strip()
        
        # Heuristic: If response is too long, it might be a paragraph. 
        # Try to find a state name inside it.
        if len(response) > 50 or response not in available_states:
            for s in available_states:
                if s.lower() in response.lower():
                    response = s
                    break
        
        self.log_call("INTERPRETER", prompt, response)
        
        if response not in available_states:
            print(f"LLM suggested '{response}', but it's not in memory. Defaulting to 'Start'.")
            response = "Start"
            
        print(f"🎯 Mapped to State: {response}")
        return {
            "current_state": response,
            "thought_process": [f"Interpreted input as state: {response}"],
            "steps": 0,
            "visited": [response]
        }

    def executor(self, state: AgentState):
        """Retrieve knowledge and execute the transition based on the current state."""
        current = state["current_state"]
        steps = state.get("steps", 0) + 1
        visited = state.get("visited", [])
        
        print("\n" + "-"*50)
        print(f"⚙️ [EXECUTOR] WORKING ON STATE: {current} (Step {steps})")
        
        if steps > 15:
            print("⚠️ WARNING: Maximum execution steps exceeded. Breaking potential loop.")
            return {
                "current_state": "END_OF_WORKFLOW",
                "steps": steps,
                "cycle_detected": False
            }
            
        if visited.count(current) > 2:
            print(f"⚠️ WARNING: Cycle detected for state '{current}'. Breaking potential loop.")
            return {
                "current_state": "END_OF_WORKFLOW",
                "steps": steps,
                "cycle_detected": True
            }
        
        # 1. Get knowledge relevant to this state AND the user input
        print(f"Searching graph for state context: '{current}'")
        kg_data = self.connector.query_kg(current)
        
        # Identify entities from user input
        print("Extracting entities from user input for deep retrieval...")
        entity_discovery_prompt = f"Identify the primary subjects or technical terms in this request: '{state['user_input']}'. Return them as a comma-separated list."
        
        discovered_entities_raw = self.llm.invoke([HumanMessage(content=entity_discovery_prompt)])
        discovered_entities_str = discovered_entities_raw.content
        self.log_call("ENTITY DISCOVERY", entity_discovery_prompt, discovered_entities_str)
        
        discovered_entities = discovered_entities_str.split(",")
        
        for ent in discovered_entities:
            ent = ent.strip().strip('"\'')
            if ent:
                found = self.connector.query_kg(ent)
                if found:
                    print(f"  ✅ Found memory for entity '{ent}': {len(found)} relations")
                    kg_data.extend(found)
                else:
                    print(f"  ❌ No specific memory for entity '{ent}'")
        
        print(f"Total facts retrieved for this step: {len(kg_data)}")
        
        # 2. Get the next transition from Procedural Map
        with self.connector.driver.session() as session:
            query = "MATCH (cs:State {name: $current})-[t:TRANSITION]->(ns) RETURN t.action as action, ns.name as next_state"
            result = session.run(query, current=current).single()
        
        if result:
            action = result["action"]
            next_state = result["next_state"]
            print(f"Next Procedure Step: {action}")
            print(f"Transitioning to State: {next_state}")
            
            execution_prompt = f"""
            Action to perform: {action}
            Knowledge found in Graph: {kg_data}
            Context: The user wants to {state['user_input']}
            
            Summarize how we perform this action using the knowledge above.
            """
            
            summary_raw = self.llm.invoke([HumanMessage(content=execution_prompt)])
            summary = summary_raw.content.strip()
            self.log_call("EXECUTION", execution_prompt, summary)
            
            return {
                "current_state": next_state,
                "graph_results": state["graph_results"] + [str(kg_data)],
                "thought_process": state["thought_process"] + [f"Executed: {action}. Result: {summary[:50]}..."],
                "history": state["history"] + [summary],
                "steps": steps,
                "visited": visited + [next_state]
            }
        
        print("No further transitions found in the procedural map.")
        return {
            "current_state": "END_OF_WORKFLOW",
            "graph_results": state["graph_results"] + [str(kg_data)],
            "steps": steps,
            "visited": visited
        }

    def router(self, state: AgentState):
        """Decide if we should continue the workflow."""
        if state["current_state"] == "END_OF_WORKFLOW" or state["current_state"] == "Task execution completed":
            return "finish"
        return "continue"

    def synthesizer(self, state: AgentState):
        """Create the final answer for the user."""
        print("\n" + "🏁 [SYNTHESIZER] GENERATING FINAL REPORT")
        
        # If no specific graph results were found, let's look at the most recent nodes
        relevant_kg = [res for res in state["graph_results"] if res != "[]"]
        
        if not relevant_kg:
            print("Graph search was shallow. Pulling most recent learning for context...")
            with self.connector.driver.session() as session:
                recent_nodes = session.run("MATCH (n:Entity) RETURN n.name as name ORDER BY id(n) DESC LIMIT 10")
                recent_list = [r["name"] for r in recent_nodes]
                relevant_kg.append(f"Recent knowledge includes: {recent_list}")
        
        print(f"Knowledge fed to final synthesis: {len(relevant_kg)} sources")

        chat_history = state.get("chat_history", [])
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history])

        final_prompt = f"""
        Conversation History:
        {chat_history_str}
        
        Original Request: {state['user_input']}
        Knowledge retrieved from Graph: {relevant_kg}
        Execution Steps & Outputs: {state['history']}
        
        Provide a concise, final report following these rules:
        1. If code is requested, provide the FULL functional code block.
        2. MANDATORY: Do NOT use placeholders like 'pass', '// add logic here', or '...'. 
        3. Use the 'Knowledge retrieved from Graph' to fill in all implementation details. 
        4. If the graph mentions a specific module (like 'os' or 'subprocess'), ensure it is imported and used in the code.
        5. Briefly explain how the graph knowledge guided the implementation.
        """
        
        response_raw = self.llm.invoke([HumanMessage(content=final_prompt)])
        response = response_raw.content
        self.log_call("SYNTHESIZER", final_prompt, response)

        # Comparative Efficiency Report
        # Standard RAG/LLM would send the whole document context (~self.graph_context_size) 
        # plus the prompt and generation for every query.
        baseline_total = self.graph_context_size + (len(state['user_input']) // 4) + (len(response) // 4)
        
        print("\n" + "📊 [COMPARATIVE EFFICIENCY REPORT]")
        print(f"Scenario A: Standard LLM (Full Context) -> {baseline_total} tokens")
        print(f"Scenario B: SiliconBrain (Sparse Graph) -> {self.total_tokens_est} tokens")
        print("-" * 40)
        savings = baseline_total - self.total_tokens_est
        ratio = (savings / baseline_total) * 100 if baseline_total > 0 else 0
        print(f"🔥 TOTAL TOKENS SAVED: {max(0, savings)}")
        print(f"🚀 COMPUTE REDUCTION: {round(ratio, 2)}%")
        print(f"🔋 ENERGY PROFILE: {self.provider == 'LOCAL (20W)' and '~20 Watts' or 'API/Cloud Watts'}")
        print("-" * 40 + "\n")
        
        return {
            "final_response": response,
            "efficiency_metrics": {
                "baseline_total": baseline_total,
                "sparse_total": self.total_tokens_est,
                "savings": max(0, savings),
                "reduction_ratio": round(ratio, 2),
                "energy_profile": self.provider == 'LOCAL (20W)' and '~20 Watts' or 'API/Cloud Watts'
            }
        }

    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("interpreter", self.interpreter)
        workflow.add_node("executor", self.executor)
        workflow.add_node("synthesizer", self.synthesizer)
        
        workflow.set_entry_point("interpreter")
        workflow.add_edge("interpreter", "executor")
        
        workflow.add_conditional_edges(
            "executor",
            self.router,
            {
                "continue": "executor",
                "finish": "synthesizer"
            }
        )
        
        workflow.add_edge("synthesizer", END)
        return workflow.compile()

if __name__ == "__main__":
    brain = SiliconBrainPhase3()
    app = brain.build_graph()
    query = "Tell me what you know about Python"
    inputs = {"user_input": query, "history": [], "thought_process": [], "graph_results": []}
    final_state = app.invoke(inputs)
    print("\n--- FINAL REPORT ---")
    print(final_state["final_response"])
    brain.connector.close()
