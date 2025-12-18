import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Environment configuration
TOOL_BASE_URL = os.getenv("TOOL_BASE_URL", "http://localhost:8000")

# LLM Configuration
# Set USE_OPENAI=true to use OpenAI, otherwise uses Ollama
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI settings (used when USE_OPENAI=true)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# Ollama settings (used when USE_OPENAI=false)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# Debug logging
print(f"[CONFIG] TOOL_BASE_URL: {TOOL_BASE_URL}")
print(f"[CONFIG] USE_OPENAI: {USE_OPENAI}")
if USE_OPENAI:
    print(f"[CONFIG] OPENAI_MODEL: {OPENAI_MODEL}")
    print(f"[CONFIG] OPENAI_API_KEY: {'***' + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'NOT SET'}")
else:
    print(f"[CONFIG] OLLAMA_URL: {OLLAMA_URL}")
    print(f"[CONFIG] OLLAMA_MODEL: {OLLAMA_MODEL}")
print(f"[CONFIG] .env path: {env_path}, exists: {env_path.exists()}")
