import time
import json
import requests
from layers.graph_connector import MemgraphConnector
from config import get_teacher_settings

class BulkLearner:
    def __init__(self):
        self.settings = get_teacher_settings()
        self.connector = MemgraphConnector()
        self.api_url = f"{self.settings['base_url']}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.settings['api_key']}",
            "Content-Type": "application/json"
        }

    def learn_topic_fast(self, topic: str):
        print(f"\n⚡ [BULK] Mastering: {topic}")
        
        prompt = f"""
        Extract high-fidelity technical intelligence about '{topic}' in Python.
        Output ONLY a JSON object with:
        1. 'knowledge_graph': 15-20 technical {{"subject", "predicate", "object"}} triplets.
        2. 'procedural_map': 3-5 key {{"current_state", "action", "next_state"}} transitions.
        
        Return ONLY valid JSON. No conversational text.
        """

        payload = {
            "model": self.settings['model'],
            "messages": [
                {"role": "system", "content": "You are a high-speed data extraction engine for a graph database."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()["choices"][0]["message"]["content"]
            intelligence = json.loads(data)
            
            # Ingest
            for triple in intelligence.get("knowledge_graph", []):
                self.connector.add_triple(triple["subject"], triple["predicate"], triple["object"])
            for step in intelligence.get("procedural_map", []):
                self.connector.add_procedure(step["current_state"], step["action"], 
                                        step["next_state"], step.get("required_knowledge", []))
            
            print(f"✅ Ingested {len(intelligence.get('knowledge_graph', []))} facts about {topic}")
        except Exception as e:
            print(f"❌ Failed to learn {topic}: {e}")

    def run_curriculum(self, topics):
        print(f"--- Starting Bulk Ingestion of {len(topics)} topics ---")
        start_time = time.time()
        for topic in topics:
            self.learn_topic_fast(topic)
            time.sleep(1) # Small delay for stability
        
        end_time = time.time()
        print(f"\n--- Curriculum Complete in {round(end_time - start_time, 2)} seconds ---")
        self.connector.close()

if __name__ == "__main__":
    python_expert_curriculum = [
        "Python Memory Management and PyObject header",
        "The Global Interpreter Lock (GIL) and its impact",
        "Python Garbage Collection: Refcounting and Generational GC",
        "Abstract Syntax Trees (AST) in Python",
        "Python Bytecode and the 'dis' module",
        "The Python Virtual Machine (PVM) loop",
        "Asynchronous Programming and the Event Loop",
        "Metaclasses and Type Creation",
        "Decorators and Closure implementation",
        "Iterators and Generators internals",
        "Python Import System and sys.modules",
        "Descriptor Protocol (get, set, delete)",
        "Dunder Methods and Data Model",
        "Multi-threading vs Multi-processing in Python",
        "C-Extensions and the Python C-API",
        "Context Managers and the 'with' statement",
        "Type Hinting and Static Analysis",
        "Functional Programming: Map, Filter, Reduce, Partial",
        "Performance Profiling (cProfile, timeit)",
        "The 'match-case' structural pattern matching"
    ]
    
    learner = BulkLearner()
    learner.run_curriculum(python_expert_curriculum)
