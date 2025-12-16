from fastapi import APIRouter

from src.orchestrator import orchestrate_chat
from src.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])

# ----------------------------
# Chat API endpoint
# ----------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Chat endpoint that delegates to the orchestrator.
    
    Handles user messages, routes them through query compilation,
    and returns UI specifications for the frontend.
    """
    return await orchestrate_chat(req)