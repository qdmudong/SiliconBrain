# SiliconBrain Troubleshooting Guide

## Problem: Ollama Connection Error
* **Definition:** The agent cannot reach the local LLM server.
* **Knowledge:** Ollama runs on port 11434 by default.
* **Knowledge:** The base URL for the OpenAI-compatible API is `http://localhost:11434/v1`.

## Procedure: Fixing Ollama Connection
1. **Start:** Check if Ollama is running.
2. **Action:** Run `ollama serve` in the terminal.
3. **Next State:** Verification.
4. **Action:** Run `curl http://localhost:11434/api/tags` to check available models.
5. **Next State:** Resolved.
