from datetime import datetime

from app.application.dtos.session_dtos import (
    CreateSessionDTO,
    SessionResponseDTO,
    UpdateSessionDTO,
)
from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import SessionRepository


class CreateSessionUseCase:
    def __init__(self, repository: SessionRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateSessionDTO) -> SessionResponseDTO:
        session = Session(
            student_id=dto.student_id,
            platform=dto.platform,
            condition=dto.condition,
            difficulty_level=dto.difficulty_level,
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
        if dto.difficulty_level is not None:
            session.difficulty_level = dto.difficulty_level
        if dto.metadata is not None:
            session.metadata.update(dto.metadata)
        updated = await self._repo.update(session)
        return _to_response(updated)


def _to_response(s: Session) -> SessionResponseDTO:
    return SessionResponseDTO(
        id=s.id,
        student_id=s.student_id,
        platform=s.platform,
        condition=s.condition,
        difficulty_level=s.difficulty_level,
        started_at=s.started_at.isoformat(),
        ended_at=s.ended_at.isoformat() if s.ended_at else None,
        status=s.status,
        metadata=s.metadata,
    )
