"""Use case orchestrating domain + repository ports.

Pillar: Stable Core
Phase: B
Purpose: Use case orchestrating domain + repository ports.
Documented in: plan/architecture.md
"""

from app.application.dtos.telemetry_dtos import (
    CreateTelemetryDTO,
    TelemetryResponseDTO,
)
from app.domain.entities.telemetry import TelemetryEvent
from app.domain.interfaces.telemetry_repository import TelemetryRepository


class IngestTelemetryUseCase:
    def __init__(self, repository: TelemetryRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateTelemetryDTO) -> TelemetryResponseDTO:
        event = TelemetryEvent(
            session_id=dto.session_id,
            student_id=dto.student_id,
            event_type=dto.event_type,
            duration_ms=dto.duration_ms,
            planet=dto.planet,
            section=dto.section,
            content=dto.content,
            help_text=dto.help_text,
            bot_type=dto.bot_type,
            payload=dto.payload,
        )
        created = await self._repo.create(event)
        return _to_response(created)


class ListSessionTelemetryUseCase:
    def __init__(self, repository: TelemetryRepository) -> None:
        self._repo = repository

    async def execute(
        self, session_id: str, limit: int = 500
    ) -> list[TelemetryResponseDTO]:
        events = await self._repo.list_by_session(session_id, limit=limit)
        return [_to_response(e) for e in events]


def _to_response(e: TelemetryEvent) -> TelemetryResponseDTO:
    return TelemetryResponseDTO(
        id=e.id,
        session_id=e.session_id,
        student_id=e.student_id,
        event_type=e.event_type,
        timestamp=e.timestamp.isoformat(),
        duration_ms=e.duration_ms,
        planet=e.planet,
        section=e.section,
        content=e.content,
        help_text=e.help_text,
        bot_type=e.bot_type,
        payload=e.payload,
    )
