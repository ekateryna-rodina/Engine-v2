import re
import httpx
from src.query_spec_builder import OLLAMA_URL
from src.schemas import QuerySpec
from v2.orchestrator_app import OLLAMA_MODEL

from typing import overload, Literal

async def query_spec_call_llm(system_prompt: str, user_message: str) -> QuerySpec:
        async with httpx.AsyncClient(timeout=45) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "format": "json",
            }
            r = await client.post(OLLAMA_URL, json=payload)
            r.raise_for_status()
            content = r.json()["message"]["content"]
            m = re.search(r"\{.*\}", content, flags=re.S)
            if not m:
                raise ValueError("No JSON found in Ollama output")
            return QuerySpec.model_validate_json(m.group(0))