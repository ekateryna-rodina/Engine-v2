import os

# Environment configuration
TOOL_BASE_URL = os.getenv("TOOL_BASE_URL", "http://localhost:8000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
