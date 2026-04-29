"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: Repository port (Clean Architecture).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.agent_action import AgentAction


class AgentActionRepository(ABC):
    """Port for agent action persistence."""

    @abstractmethod
    async def create(self, action: AgentAction) -> AgentAction: ...

    @abstractmethod
    async def get_by_id(
        self, action_id: str, session_id: str
    ) -> AgentAction | None: ...

    @abstractmethod
    async def list_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[AgentAction]: ...
