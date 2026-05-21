# 🧠 SiliconBrain: The 20-Watt General-Purpose Expert

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Memgraph](https://img.shields.io/badge/database-Memgraph-red.svg)](https://memgraph.com/)
[![Ollama](https://img.shields.io/badge/local%20LLM-Ollama-black.svg)](https://ollama.com/)

SiliconBrain is a high-performance **Neuro-Symbolic Framework** designed to run on local hardware with the efficiency of a human brain (~20 Watts). By separating **Declarative Knowledge** (Facts in a Graph Database) from **Procedural Logic** (State Machines), SiliconBrain enables tiny local models to achieve the reasoning capabilities of trillion-parameter giants.

![Knowledge Map Demo](assets/knowledge_map_demo.png)

## 💡 Quick Walkthrough: From Learning to Generation

Here is a typical end-to-end flow of how SiliconBrain operates:

1. **Train the Brain (Mastery):** You ask the **Mastery Engine** to learn many Python topics (e.g., *"Python Memory Management and PyObject header"*). The system interrogates a high-IQ Teacher LLM, extracts declarative facts (triples) and procedural workflow steps, and writes them to the local **Memgraph** database. **After adequate training, the brain will have accumulated a rich Python knowledge base.**
2. **Generate Python Scripts:** When you ask the agent, *"Write a script that accesses a PyObject header to inspect refcounts,"* the orchestrator intercepts the query.
3. **Save 90%+ Tokens:** Instead of feeding hundreds of lines of raw manuals or documentation context to the LLM (dense retrieval), SiliconBrain performs **sparse graph activation**. It retrieves only the specific nodes and relationships related to your request from the graph, saving significant token overhead and allowing a tiny local model like llama3.2:3b to write fully correct code instantly.

---

## 🚧 Project Status: Proof of Concept

SiliconBrain is a **functional research prototype** of a general-purpose Neuro-Symbolic AI system. While it ships with a massive pre-loaded library for software engineering, the underlying architecture is designed to **master any technical or creative domain** autonomously.

---

## 🚀 Key Features

*   **Domain-Agnostic Mastery:** Use the Mastery Engine to "download" expert-level knowledge in any field (Medicine, Law, Engineering, etc.) into a local graph database.
*   **Sparse Activation:** Saves **up to 90% in tokens** by only retrieving relevant graph nodes instead of feeding massive raw text contexts to the LLM.
*   **Autonomous Curiosity Engine:** Features a background loop that identifies gaps in its own knowledge, ponders what it needs to learn next, and bridges those gaps automatically.
*   **20-Watt Local Mode:** Designed to run the primary chat orchestration on your local CPU (via Ollama) while leveraging high-IQ reasoning models (via DeepSeek) for background learning.
*   **Visual Reasoning:** Interactive **Knowledge Map Viewer** (via PyVis) lets you explore the brain's evolving memory and state transitions directly in your browser.

---

## 🗺️ System Architecture

SiliconBrain splits cognitive tasks into two distinct layers:
1.  **The "What" Layer (Declarative):** Structured triplets (`{subject, predicate, object}`) stored in **Memgraph**.
2.  **The "How" Layer (Procedural):** Structured state transitions (`{current_state, action, next_state}`) orchestrating workflows via **LangGraph**.

```mermaid
graph TD
    User([User Query]) --> Interpreter[Interpreter Node: Maps intent to State]
    Interpreter --> Executor[Executor Node: Queries KG & runs transitions]
    Executor --> DB[(Memgraph DB)]
    Executor --> Synthesizer[Synthesizer Node: Compiles final response]
    Synthesizer --> User
    
    subgraph Learning Loop
        Teacher[Teacher LLM: DeepSeek API] --> Extractor[Librarian: layers/extractor.py]
        Extractor --> DB
        Curiosity[Curiosity Engine: layers/curiosity.py] -->|1. Identifies Gaps| Teacher
    end
```

### Core Components:
*   **The Orchestrator ([layers/orchestration_v2.py](layers/orchestration_v2.py)):** A LangGraph agent that performs sparse graph retrieval to answer user queries with minimal token usage.
*   **The Librarian ([layers/extractor.py](layers/extractor.py)):** Parses raw explanation texts and distills them into structured entity triplets and state-transition schemas.
*   **The Teacher Interface ([layers/teacher.py](layers/teacher.py)):** Queries a high-IQ LLM to explain complex domains.
*   **The Curiosity Engine ([layers/curiosity.py](layers/curiosity.py)):** Shuffles current database entities, ponders knowledge gaps, and schedules new topics for the Teacher to distill.

---

## 📦 Pre-Loaded: Software Engineering Knowledge Pack

As a demonstration of its power, this repository includes a pre-trained memory of **15,000+ nodes** covering the deep-lore and architectural patterns of:
*   **Python:** Internals, DDD, Performance, and Meta-programming.
*   **Rust:** Ownership, Fearless Concurrency, and Async internals.
*   **TypeScript:** Advanced Type System, Compiler API, and Full-stack patterns.

---

## 🔋 The Efficiency Proof

SiliconBrain includes a live **Efficiency Report** in the dashboard comparing:
*   **Scenario A:** Standard LLM (Full-Context RAG)
*   **Scenario B:** SiliconBrain (Sparse Graph Retrieval)

For complex technical queries, Scenario B typically demonstrates a **10x reduction in compute requirements** (90%+ tokens saved) by loading only the localized neighborhood of nodes relative to the user's intent.

---

## 🛠️ Quick Start

### 1. Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Ollama](https://ollama.com/) (Ensure the daemon is running and you have `llama3.2:3b` or your preferred local model pulled)

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
# Edit .env and configure your API keys and model preferences
```

### 3. Inject the Pre-Trained Brain
Ensure Memgraph is running, then run the injection command to load the 15,000+ node software engineering knowledge pack:
```bash
# Start the Knowledge Graph container
docker-compose up -d

# Inject cypher snapshot
cat data/trained_brain.cypher | docker exec -i memgraph mgconsole --output_format=cypherl
```

### 4. Launch the Dashboard
```bash
streamlit run dashboard.py
```
Open your browser to `http://localhost:8501` to chat with the brain, view the interactive visual map, or launch recursive mastery engines.

---

## 🛠️ Troubleshooting

*   **Docker Connection:** If you encounter `Connection Refused` errors, make sure Docker Desktop is active and `docker ps` shows the `memgraph` container running on port `7687`.
*   **Ollama Connection:** Verify your Ollama instance is serving on the default port `11434` (SiliconBrain connects to Ollama via `http://localhost:11434/v1`).
*   **Teacher API Keys:** Ensure your DeepSeek API key is correctly configured in your `.env` file for the background learner to operate.

---
*Created with the vision of efficient, grounded, and local-first intelligence.*
