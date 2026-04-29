"""
LLM Provider abstraction layer.

Defines the interface that all LLM backends must implement.
This allows switching between Ollama (local dev), Azure AI Foundry (production),
or any other provider via configuration — without changing agent code.

Pillar: Stable Core
Phase: E
Purpose: Abstract LLMProvider port.
Documented in: docs/decisions.md
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """A single message in a chat conversation."""

    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str = ""
    usage: dict = field(default_factory=dict)  # {prompt_tokens, completion_tokens, total_tokens}


class LLMProvider(ABC):
    """Abstract interface for LLM backends."""

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Send a chat completion request."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        ...
