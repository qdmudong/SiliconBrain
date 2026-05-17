import json
import requests
from layers.schema import HybridMap

from config import get_teacher_settings

settings = get_teacher_settings()
OLLAMA_URL = f"{settings['base_url']}/chat/completions" # Standard OpenAI endpoint
MODEL_NAME = settings['model']
API_KEY = settings['api_key']

SYSTEM_PROMPT = """
You are the 'SiliconBrain Librarian'. Your job is to extract structured intelligence from text.
You must output a JSON object that adheres to the following schema:
- 'knowledge_graph': A list of {subject, predicate, object} triples representing facts and concepts.
- 'procedural_map': A list of {current_state, action, next_state, required_knowledge} representing workflows and logic.

Strictly output ONLY valid JSON.
"""

def extract_intelligence(text: str) -> dict:
    prompt = f"Analyze the following text and extract knowledge triplets and procedural steps. Output the result as a single JSON object. Do not include any other text.\n\nText:\n{text}\n\nJSON Output:"
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    print(f"\n--- LLM REQUEST (EXTRACTOR) ---")
    print(f"URL: {OLLAMA_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Prompt Sent: {prompt[:500]}...")
    
    response = requests.post(OLLAMA_URL, headers=headers, json=payload)
    print(f"Status code: {response.status_code}")
    response.raise_for_status()
    
    raw_response = response.json()["choices"][0]["message"]["content"].strip()
    print(f"\n--- LLM RESPONSE (EXTRACTOR) ---")
    print(f"Raw Content: {raw_response[:500]}...")
    print(f"--------------------------------\n")
    
    # Robustly find JSON in the response
    import re
    json_match = re.search(r'(\{.*\})', raw_response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = raw_response

    # Remove potential thinking or markdown markers
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0].strip()
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0].strip()
        
    print(f"Cleaned JSON (first 100 chars): {json_str[:100]}...")
    return json.loads(json_str)

if __name__ == "__main__":
    with open("AI_Intelligence_Project_Manifesto.md", "r") as f:
        manifesto = f.read()
    
    print(f"Extracting intelligence from Manifesto using {MODEL_NAME}...")
    try:
        intelligence = extract_intelligence(manifesto)
        with open("data/manifesto_extracted.json", "w") as f:
            json.dump(intelligence, f, indent=4)
        print("Successfully extracted intelligence to data/manifesto_extracted.json")
    except Exception as e:
        print(f"Extraction failed: {e}")
