"""
Azure AI Foundry LLM Provider — for production and cloud testing.

Uses Azure OpenAI endpoints via the openai SDK with Azure-specific auth.
Requires: azure_openai_endpoint, azure_openai_key, deployment names in config.
"""

import logging

from openai import AsyncAzureOpenAI

from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class AzureFoundryProvider(LLMProvider):
    """LLM provider backed by Azure AI Foundry / Azure OpenAI."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        chat_deployment: str,
        embedding_deployment: str,
        api_version: str = "2024-12-01-preview",
    ) -> None:
        self._client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        self._chat_deployment = chat_deployment
        self._embedding_deployment = embedding_deployment

    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        resp = await self._client.chat.completions.create(
            model=self._chat_deployment,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0]
        usage = resp.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=self._chat_deployment,
            usage={
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
        )

    async def embed(self, text: str) -> list[float]:
        resp = await self._client.embeddings.create(
            model=self._embedding_deployment,
            input=text,
        )
        return resp.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.embeddings.create(
            model=self._embedding_deployment,
            input=texts,
        )
        return [item.embedding for item in resp.data]
