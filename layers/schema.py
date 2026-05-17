import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Triple(BaseModel):
    subject: str = Field(..., description="The entity being described")
    predicate: str = Field(..., description="The relationship between subject and object")
    object: str = Field(..., description="The target entity or value")

class StateTransition(BaseModel):
    current_state: str = Field(..., description="The current state in the workflow")
    action: str = Field(..., description="The action that triggers the transition")
    next_state: str = Field(..., description="The resulting state")
    required_knowledge: List[str] = Field(default_factory=list, description="Entities/concepts from the KG required for this step")

class HybridMap(BaseModel):
    knowledge_graph: List[Triple] = Field(..., description="Declarative 'What' layer")
    procedural_map: List[StateTransition] = Field(..., description="Procedural 'How' layer")

def save_schema():
    schema = HybridMap.model_json_schema()
    with open("data/semantic_protocol.json", "w") as f:
        json.dump(schema, f, indent=4)
    print("Semantic Protocol schema saved to data/semantic_protocol.json")

if __name__ == "__main__":
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    save_schema()
