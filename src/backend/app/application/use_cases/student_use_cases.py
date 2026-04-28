from app.application.dtos.student_dtos import (
    CreateStudentDTO,
    IdentifyStudentDTO,
    StudentResponseDTO,
)
from app.domain.entities.student import Student
from app.domain.interfaces.student_repository import StudentRepository


class IdentifyOrCreateStudentUseCase:
    """Idempotent: returns the existing student for ``(platform, platform_user_id)``
    or creates one if absent. This is the entry point every VR/web client calls
    on first interaction.
    """

    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: IdentifyStudentDTO) -> StudentResponseDTO:
        existing = await self._repo.get_by_platform_identity(
            dto.platform, dto.platform_user_id
        )
        if existing is not None:
            return _to_response(existing)
        student = Student(
            platform=dto.platform,
            platform_user_id=dto.platform_user_id,
            display_name=dto.display_name,
            metadata=dto.metadata,
        )
        created = await self._repo.create(student)
        return _to_response(created)


class CreateStudentUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateStudentDTO) -> StudentResponseDTO:
        student = Student(
            platform=dto.platform,
            platform_user_id=dto.platform_user_id,
            display_name=dto.display_name,
            metadata=dto.metadata,
        )
        created = await self._repo.create(student)
        return _to_response(created)


class GetStudentUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, student_id: str) -> StudentResponseDTO | None:
        student = await self._repo.get_by_id(student_id)
        if not student:
            return None
        return _to_response(student)


class ListStudentsUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(
        self, limit: int = 50, offset: int = 0
    ) -> list[StudentResponseDTO]:
        students = await self._repo.list_all(limit=limit, offset=offset)
        return [_to_response(s) for s in students]


def _to_response(s: Student) -> StudentResponseDTO:
    return StudentResponseDTO(
        id=s.id,
        platform=s.platform,
        platform_user_id=s.platform_user_id,
        display_name=s.display_name,
        created_at=s.created_at.isoformat(),
        metadata=s.metadata,
    )
