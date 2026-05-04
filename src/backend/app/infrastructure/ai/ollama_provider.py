"""
Ollama LLM Provider - default local/self-hosted runtime.

Uses the Ollama REST API (default: http://localhost:11434).
Requires Ollama running locally with models pulled (e.g., llama3, nomic-embed-text).

Pillar: Stable Core
Phase: E
Purpose: Local/self-hosted Ollama implementation of LLMProvider (Phase OL static-IP).
Documented in: docs/deployment/ollama-network.md
"""

import logging

import httpx

from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider, LLMResponse
from app.infrastructure.ai.registry import LLMProviderRegistry

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider backed by a local Ollama instance."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        chat_model: str = "llama3",
        embedding_model: str = "nomic-embed-text",
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._timeout = timeout

    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        payload = {
            "model": self._chat_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data.get("message", {}).get("content", ""),
            model=self._chat_model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": (
                    data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                ),
            },
        )

    async def embed(self, text: str) -> list[float]:
        payload = {"model": self._embedding_model, "input": text}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base_url}/api/embed", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["embeddings"][0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self._embedding_model, "input": texts}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base_url}/api/embed", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["embeddings"]


@LLMProviderRegistry.register("ollama")
def _build_ollama_provider(settings):
    return OllamaProvider(
        base_url=settings.ollama_base_url,
        chat_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embedding_model,
    )
