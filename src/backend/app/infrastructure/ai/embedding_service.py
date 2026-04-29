"""
Embedding service — thin wrapper over the LLM provider's embedding capability.

Used by the knowledge ingestion pipeline and the Content Curation Agent
for RAG vector search.

Pillar: Stable Core
Phase: E
Purpose: Embedding helper for RAG ingestion + vector search.
Documented in: docs/decisions.md
"""

from app.infrastructure.ai.llm_provider import LLMProvider


class EmbeddingService:
    """Generates text embeddings using the configured LLM provider."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def embed(self, text: str) -> list[float]:
        return await self._provider.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return await self._provider.embed_batch(texts)
