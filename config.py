import os
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# --- PROVIDER CONFIGURATION ---
# Options: "ollama" or "deepseek"
ORCHESTRATOR_PROVIDER = os.getenv("ORCHESTRATOR_PROVIDER", "ollama")
TEACHER_PROVIDER = os.getenv("TEACHER_PROVIDER", "deepseek")

# --- DEEPSEEK SETTINGS ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = os.getenv("TEACHER_MODEL", "deepseek-v4-flash")

# --- OLLAMA SETTINGS ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gpt-oss:20b")

def get_orchestrator_settings():
    if ORCHESTRATOR_PROVIDER == "deepseek":
        return get_deepseek_settings()
    return get_ollama_settings()

def get_teacher_settings():
    if TEACHER_PROVIDER == "deepseek":
        return get_deepseek_settings()
    return get_ollama_settings()

def get_deepseek_settings():
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_key_here":
        print("WARNING: DeepSeek API Key not found. Falling back to Ollama.")
        return get_ollama_settings()
    return {
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_BASE_URL,
        "model": DEEPSEEK_MODEL
    }

def get_ollama_settings():
    return {
        "api_key": "ollama",
        "base_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL
    }

# Legacy support for old calls
def get_llm_settings():
    return get_orchestrator_settings()
