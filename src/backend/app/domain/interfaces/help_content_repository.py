"""Static help content repository port.

Pillar: Scenario Pack
Phase: S
Purpose: Static help content repository port.
Documented in: data/help_content/README.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.help_content import HelpContent


class HelpContentRepository(ABC):
    """Port for static help content persistence."""

    @abstractmethod
    async def create(self, content: HelpContent) -> HelpContent: ...

    @abstractmethod
    async def update(self, content: HelpContent) -> HelpContent: ...

    @abstractmethod
    async def get_by_id(self, content_id: str, planet: str) -> HelpContent | None: ...

    @abstractmethod
    async def query(
        self,
        planet: str,
        section: str | None = None,
        content_topic: str | None = None,
        difficulty_level: str | None = None,
        help_type: str | None = None,
        limit: int = 50,
    ) -> list[HelpContent]: ...

    @abstractmethod
    async def list_planets(self) -> list[str]: ...
