from fastapi import APIRouter, Depends, HTTPException

from app.application.dtos.student_dtos import CreateStudentDTO, StudentResponseDTO
from app.application.use_cases.student_use_cases import (
    CreateStudentUseCase,
    GetStudentUseCase,
    ListStudentsUseCase,
)
from app.dependencies import get_student_repository

router = APIRouter()


@router.post("", response_model=StudentResponseDTO, status_code=201)
async def create_student(dto: CreateStudentDTO):
    repo = get_student_repository()
    use_case = CreateStudentUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{student_id}", response_model=StudentResponseDTO)
async def get_student(student_id: str):
    repo = get_student_repository()
    use_case = GetStudentUseCase(repo)
    result = await use_case.execute(student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.get("", response_model=list[StudentResponseDTO])
async def list_students(limit: int = 50, offset: int = 0):
    repo = get_student_repository()
    use_case = ListStudentsUseCase(repo)
    return await use_case.execute(limit=limit, offset=offset)
