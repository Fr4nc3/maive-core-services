from app.domain.entities.student import Student
from app.domain.interfaces.student_repository import StudentRepository
from app.application.dtos.student_dtos import CreateStudentDTO, StudentResponseDTO


class CreateStudentUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateStudentDTO) -> StudentResponseDTO:
        student = Student(
            email=dto.email,
            display_name=dto.display_name,
            group=dto.group,
            metadata=dto.metadata,
        )
        created = await self._repo.create(student)
        return StudentResponseDTO(
            id=created.id,
            email=created.email,
            display_name=created.display_name,
            group=created.group,
            created_at=created.created_at.isoformat(),
            metadata=created.metadata,
        )


class GetStudentUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(self, student_id: str) -> StudentResponseDTO | None:
        student = await self._repo.get_by_id(student_id)
        if not student:
            return None
        return StudentResponseDTO(
            id=student.id,
            email=student.email,
            display_name=student.display_name,
            group=student.group,
            created_at=student.created_at.isoformat(),
            metadata=student.metadata,
        )


class ListStudentsUseCase:
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository

    async def execute(
        self, limit: int = 50, offset: int = 0
    ) -> list[StudentResponseDTO]:
        students = await self._repo.list_all(limit=limit, offset=offset)
        return [
            StudentResponseDTO(
                id=s.id,
                email=s.email,
                display_name=s.display_name,
                group=s.group,
                created_at=s.created_at.isoformat(),
                metadata=s.metadata,
            )
            for s in students
        ]
