from fastapi import FastAPI
from .tools_api import router as tools_router

app = FastAPI(title="Orchestrator (QuerySpec -> tools -> compute -> UISpec)")
app.include_router(tools_router)