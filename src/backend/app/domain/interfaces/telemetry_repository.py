"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: Repository port (Clean Architecture).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.telemetry import TelemetryEvent


class TelemetryRepository(ABC):
    """Port for telemetry event persistence."""

    @abstractmethod
    async def create(self, event: TelemetryEvent) -> TelemetryEvent: ...

    @abstractmethod
    async def list_by_session(
        self, session_id: str, limit: int = 500
    ) -> list[TelemetryEvent]: ...
