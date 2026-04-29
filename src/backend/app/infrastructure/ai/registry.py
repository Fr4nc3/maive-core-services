"""LLM provider registry; closes if/elif provider switch (DEC-016).

Pillar: Stable Core
Phase: P1
Purpose: LLM provider registry; closes if/elif provider switch (DEC-016).
Documented in: docs/decisions.md
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config import Settings
    from app.infrastructure.ai.llm_provider import LLMProvider


Builder = Callable[["Settings"], "LLMProvider"]


class LLMProviderRegistry:
    """Class-level registry mapping provider keys to builder callables."""

    _builders: dict[str, Builder] = {}

    @classmethod
    def register(cls, key: str) -> Callable[[Builder], Builder]:
        """Decorator used by provider modules to self-register a builder."""

        def _decorator(builder: Builder) -> Builder:
            cls._builders[key] = builder
            return builder

        return _decorator

    @classmethod
    def build(cls, key: str, settings: Settings) -> LLMProvider:
        """Instantiate the provider registered under `key`."""
        cls._ensure_loaded()
        if key not in cls._builders:
            available = ", ".join(sorted(cls._builders)) or "<none>"
            raise ValueError(
                f"Unknown LLM provider: {key!r}. Registered: {available}"
            )
        return cls._builders[key](settings)

    @classmethod
    def registered(cls) -> list[str]:
        cls._ensure_loaded()
        return sorted(cls._builders)

    @classmethod
    def _ensure_loaded(cls) -> None:
        """Import provider modules so their @register decorators run."""
        # Import side effect: each module decorates a builder on import.
        from app.infrastructure.ai import (  # noqa: F401
            azure_foundry_provider,
            ollama_provider,
        )
