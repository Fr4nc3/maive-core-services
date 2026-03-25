from app.domain.entities.student import Student
from app.domain.interfaces.student_repository import StudentRepository
from app.application.dtos.student_dtos import CreateStudentDTO, StudentResponseDTO


class CreateStudentUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateStudentDTO) -> StudentResponseDTO:
        student = Student(
            spatial_id=dto.spatial_id,
            group=dto.group,
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
        spatial_id=s.spatial_id,
        group=s.group,
        created_at=s.created_at.isoformat(),
        metadata=s.metadata,
    )
