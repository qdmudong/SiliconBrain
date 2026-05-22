import requests
import json
from layers.extractor import extract_intelligence
from layers.graph_connector import MemgraphConnector

from config import get_teacher_settings

settings = get_teacher_settings()
API_URL = f"{settings['base_url']}/chat/completions"
MODEL_NAME = settings['model']
API_KEY = settings['api_key']

class TeacherInterface:
    def __init__(self):
        self.connector = MemgraphConnector()

    def ask_teacher(self, topic: str):
        print(f"\n[TEACHER] Researching topic: {topic} using {MODEL_NAME}...")
        
        prompt = f"""
        Provide a detailed technical explanation of '{topic}'.
        Break your answer into two clear sections:
        1. DECLARATIVE KNOWLEDGE: Facts, entities, and their relationships.
        2. PROCEDURAL LOGIC: The step-by-step process of how it works or how to implement it.
        
        Be precise and technical.
        """
        
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a world-class technical expert and teacher."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        print(f"\n--- LLM REQUEST (TEACHER) ---")
        print(f"URL: {API_URL}")
        print(f"Model: {MODEL_NAME}")
        print(f"Prompt Sent: {prompt[:500]}...")

        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        
        raw_response = response.json()["choices"][0]["message"]["content"]
        print(f"\n--- LLM RESPONSE (TEACHER) ---")
        print(f"Raw Content: {raw_response[:500]}...")
        print(f"--------------------------------\n")
        return raw_response

    def distill_knowledge(self, topic: str):
        # 1. Get the raw knowledge from the 'Teacher'
        raw_explanation = self.ask_teacher(topic)
        print(f"[TEACHER] Received explanation ({len(raw_explanation)} chars).")
        
        # 2. Use the 'Librarian' (Extractor) to structure it
        print(f"[LIBRARIAN] Extracting intelligence from Teacher's explanation...")
        intelligence = extract_intelligence(raw_explanation)
        
        # 3. Save to Memgraph
        kg_count = len(intelligence.get("knowledge_graph", []))
        pm_count = len(intelligence.get("procedural_map", []))
        
        print(f"[STUDENT] Learning {kg_count} facts and {pm_count} procedures about {topic}...")
        
        learned_facts = []
        for triple in intelligence.get("knowledge_graph", []):
            if all(k in triple for k in ["subject", "predicate", "object"]):
                self.connector.add_triple(triple["subject"], triple["predicate"], triple["object"])
                learned_facts.append(f"{triple['subject']} {triple['predicate']} {triple['object']}")
                
        for step in intelligence.get("procedural_map", []):
            if all(k in step for k in ["current_state", "action", "next_state"]):
                self.connector.add_procedure(step["current_state"], step["action"], 
                                        step["next_state"], step.get("required_knowledge", []))
        
        print(f"[STUDENT] Mastered topic: {topic}")
        if learned_facts:
            print(f"[STUDENT] Sample learned facts: {learned_facts[:3]}...")

    def close(self):
        self.connector.close()
 
if __name__ == "__main__":
    teacher = TeacherInterface()
    try:
        # Let's learn about the core of the Manifesto
        teacher.distill_knowledge("Spiking Neural Networks and their energy efficiency")
    finally:
        teacher.close()
