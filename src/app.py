from fastapi import FastAPI
from .tools_api import router as tools_router
from .chat_api import router as chat_router

app = FastAPI(title="Orchestrator (QuerySpec -> tools -> compute -> UISpec)")
app.include_router(tools_router)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok"}