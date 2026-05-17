# 🧠 SiliconBrain: The 20-Watt Local Expert

![Knowledge Map Demo](assets/knowledge_map_demo.png)

## 🚧 Project Status: Proof of Concept
SiliconBrain is a **functional research prototype**. While the trilingual expert system is fully operational and capable of advanced architectural reasoning, it is primarily a demonstration of the **20-Watt efficiency vision**. We are currently in the "Zero-to-One" phase and invite contributors to help refine the neuro-symbolic pathways.

SiliconBrain is a high-performance
 **Neuro-Symbolic AI system** designed to run on local hardware with the efficiency of a human brain (~20 Watts).
 By separating **Declarative Knowledge** (Facts in a Graph Database) from **Procedural Logic** (State Machines), SiliconBrain enables tiny local models (like Llama 3 3B) to achieve the reasoning capabilities of trillion-parameter giants.

## 🚀 Key Features

- **Hybrid Intelligence:** Combines the factual accuracy of **Memgraph** with the agentic reasoning of **LangGraph**.
- **Sparse Activation:** Saves up to **90% in tokens** by only retrieving relevant graph nodes instead of massive raw text contexts.
- **Autonomous Learning:** Features a **Curiosity Engine** and **Recursive Domain Mastery** to build local expert libraries automatically.
- **Trilingual Mastery:** Comes pre-configured to master **Python, Rust, and TypeScript** ecosystems.
- **20-Watt Local Mode:** Designed to run the primary chat orchestration on your local CPU (via Ollama) while using high-IQ models (via DeepSeek) for background learning.

## 🛠️ Tech Stack

- **Memory:** Memgraph (Graph Database)
- **Logic:** LangGraph (State Machines)
- **Interface:** Streamlit (Web Dashboard)
- **Compute:** Ollama (Local) & DeepSeek API (Teacher)
- **Orchestration:** Python (LangChain)

## 🚦 Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) (Download `llama3.2:3b`)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/your-username/SiliconBrain.git
cd SiliconBrain

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your DeepSeek API Key
```

### 3. Launch
```bash
# Start the Knowledge Graph
docker-compose up -d

# Start the Dashboard
streamlit run dashboard.py
```

## 🛠️ Troubleshooting
- **Docker Connection:** If you see a `Connection Refused` error, ensure Docker Desktop is running and run `docker-compose up -d` to start the Memgraph container.
- **Ollama API:** Ensure `ollama serve` is active. SiliconBrain looks for Ollama on the default port `11434`.
- **API Keys:** Make sure your DeepSeek key is correctly placed in the `.env` file for the "Teacher" to function.

## 🗺️ System Architecture

1.  **The Librarian (`layers/extractor.py`):** Converts raw text/explanations into structured Triplets.
2.  **The Brain Memory:** Stores thousands of technical interconnections in Memgraph.
3.  **The Orchestrator (`layers/orchestration_v2.py`):** A LangGraph agent that performs sparse retrieval to answer queries.
4.  **The Mastery Engine:** Recursively interrogates a "Teacher" LLM to map out entire programming domains.

## 🔋 The Efficiency Proof
SiliconBrain includes a live **Efficiency Report** that compares Scenario A (Standard LLM Full-Context) vs Scenario B (SiliconBrain Sparse Graph). Most technical queries show a **10x reduction in compute requirements**.

---
*Created with the vision of efficient, grounded, and local-first intelligence.*
**10x reduction in compute requirements**.

---
*Created with the vision of efficient, grounded, and local-first intelligence.*
