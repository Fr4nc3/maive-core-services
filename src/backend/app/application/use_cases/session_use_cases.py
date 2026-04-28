from datetime import datetime

from app.application.dtos.session_dtos import (
    CreateSessionDTO,
    SessionResponseDTO,
    UpdateSessionDTO,
)
from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import SessionRepository
from app.domain.interfaces.student_repository import StudentRepository


class CreateSessionUseCase:
    def __init__(
        self,
        repository: SessionRepository,
        student_repository: StudentRepository | None = None,
    ) -> None:
        self._repo = repository
        self._student_repo = student_repository

    async def execute(self, dto: CreateSessionDTO) -> SessionResponseDTO:
        # Resolve language: explicit dto.language wins, else fall back to
        # student.preferred_language (when student repo is wired), else "en".
        # See DEC-014.
        language = dto.language
        if language is None and self._student_repo is not None:
            student = await self._student_repo.get_by_id(dto.student_id)
            if student is not None:
                language = student.preferred_language
        if not language:
            language = "en"

        session = Session(
            student_id=dto.student_id,
            platform=dto.platform,
            condition=dto.condition,
            difficulty_level=dto.difficulty_level,
            language=language,
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
        if dto.language is not None:
            session.language = dto.language
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
        language=s.language,
        started_at=s.started_at.isoformat(),
        ended_at=s.ended_at.isoformat() if s.ended_at else None,
        status=s.status,
        metadata=s.metadata,
    )
