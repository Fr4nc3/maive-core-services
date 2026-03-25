from datetime import datetime

from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import SessionRepository
from app.application.dtos.session_dtos import (
    CreateSessionDTO,
    UpdateSessionDTO,
    SessionResponseDTO,
)


class CreateSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateSessionDTO) -> SessionResponseDTO:
        session = Session(
            student_id=dto.student_id,
            condition=dto.condition,
            metadata=dto.metadata,
        )
        created = await self._repo.create(session)
        return _to_response(created)


class GetSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repo = repository

    async def execute(self, session_id: str) -> SessionResponseDTO | None:
        session = await self._repo.get_by_id(session_id)
        if not session:
            return None
        return _to_response(session)


class UpdateSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repo = repository

    async def execute(
        self, session_id: str, dto: UpdateSessionDTO
    ) -> SessionResponseDTO | None:
        session = await self._repo.get_by_id(session_id)
        if not session:
            return None
        if dto.status:
            session.status = dto.status
            if dto.status == "completed":
                session.ended_at = datetime.utcnow()
        if dto.metadata is not None:
            session.metadata.update(dto.metadata)
        updated = await self._repo.update(session)
        return _to_response(updated)


def _to_response(s: Session) -> SessionResponseDTO:
    return SessionResponseDTO(
        id=s.id,
        student_id=s.student_id,
        condition=s.condition,
        started_at=s.started_at.isoformat(),
        ended_at=s.ended_at.isoformat() if s.ended_at else None,
        status=s.status,
        metadata=s.metadata,
    )
