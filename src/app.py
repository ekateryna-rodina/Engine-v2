from fastapi import FastAPI
from contextlib import asynccontextmanager
from .tools_api import router as tools_router
from .chat_api import router as chat_router
import httpx
from src.config import OLLAMA_MODEL, OLLAMA_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warmup the LLM model on startup to keep it in memory"""
    print("=" * 60)
    print("[WARMUP] LIFESPAN STARTED - Beginning model warmup")
    print(f"[WARMUP] Model: {OLLAMA_MODEL}")
    print(f"[WARMUP] URL: {OLLAMA_URL}")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "stream": False,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
            }
            print(f"[WARMUP] Sending request to Ollama...")
            r = await client.post(OLLAMA_URL, json=payload)
            r.raise_for_status()
            print("=" * 60)
            print(f"[WARMUP] ✅ SUCCESS - Model {OLLAMA_MODEL} is loaded and ready!")
            print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"[WARMUP] ❌ FAILED - Model warmup error: {e}")
        print(f"[WARMUP] Model will be loaded on first user request")
        print("=" * 60)
    
    yield  # Application runs here
    
    # Cleanup on shutdown (if needed)
    print("[SHUTDOWN] Application shutting down")

app = FastAPI(
    title="Orchestrator (QuerySpec -> tools -> compute -> UISpec)",
    lifespan=lifespan
)
app.include_router(tools_router)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok"}