import time
import random
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from layers.graph_connector import MemgraphConnector
from layers.teacher import TeacherInterface

from config import get_orchestrator_settings

class CuriosityEngine:
    def __init__(self):
        settings = get_orchestrator_settings()
        self.connector = MemgraphConnector()
        self.teacher = TeacherInterface()
        self.llm = ChatOpenAI(
            model=settings["model"],
            base_url=f"{settings['base_url']}/v1" if "deepseek" in settings["base_url"] else settings["base_url"],
            api_key=settings["api_key"],
            temperature=0.7 # A bit of randomness for creativity
        )

    def get_known_entities(self, limit=15):
        """Fetch a random sample of things the brain already knows."""
        with self.connector.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN e.name as name")
            entities = [r["name"] for r in result]
        
        if not entities:
            return []
        
        # Shuffle and take a sample to prevent context window overload
        random.shuffle(entities)
        return entities[:limit]

    def ponder_next_topic(self) -> str:
        """Ask the LLM to identify a knowledge gap based on current memory."""
        known_concepts = self.get_known_entities()
        
        if not known_concepts:
            return "The fundamental principles of Neuro-symbolic AI"
            
        print(f"\n[CURIOSITY] Pondering my current knowledge base: {known_concepts[:5]}...")
        
        prompt = f"""
        You are the 'Curiosity Engine' of an AI system.
        The system currently has knowledge about the following concepts:
        {known_concepts}
        
        Identify ONE specific, advanced technical concept that is highly relevant to these ideas, but represents a logical "next step" in learning. It should bridge gaps or deepen the system's understanding.
        
        CRITICAL RULE: Return ONLY the name of the concept. Do not include quotes, explanations, or introductory text. Just the topic name.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)]).content.strip()
        # Clean up in case the model ignores instructions
        topic = response.split('\n')[0].strip('"\'')
        print(f"[CURIOSITY] I have decided I need to learn about: '{topic}'")
        return topic

    def autonomous_learning_loop(self, iterations=3):
        print(f"--- SiliconBrain Curiosity Engine Started ({iterations} Iterations) ---")
        for i in range(iterations):
            print(f"\n--- Learning Cycle {i+1}/{iterations} ---")
            
            # 1. Ponder what to learn next
            new_topic = self.ponder_next_topic()
            
            # 2. Use the Teacher to learn it
            try:
                self.teacher.distill_knowledge(new_topic)
            except Exception as e:
                print(f"[CURIOSITY] Failed to learn {new_topic} due to an error: {e}")
                print("[CURIOSITY] Moving to the next thought...")
            
            # Brief pause to cool down the local LLM
            if i < iterations - 1:
                print("[CURIOSITY] Digesting knowledge for 5 seconds...")
                time.sleep(5)
                
        print("\n--- Curiosity Cycle Complete ---")
        self.connector.close()

if __name__ == "__main__":
    engine = CuriosityEngine()
    engine.autonomous_learning_loop(iterations=2)
