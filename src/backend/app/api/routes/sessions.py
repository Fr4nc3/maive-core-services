"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter, HTTPException

from app.application.dtos.session_dtos import (
    CreateSessionDTO,
    SessionResponseDTO,
    UpdateSessionDTO,
)
from app.application.use_cases.session_use_cases import (
    CreateSessionUseCase,
    GetSessionUseCase,
    UpdateSessionUseCase,
)
from app.dependencies import get_session_repository, get_student_repository

router = APIRouter()


@router.post("", response_model=SessionResponseDTO, status_code=201)
async def create_session(dto: CreateSessionDTO):
    repo = get_session_repository()
    student_repo = get_student_repository()
    use_case = CreateSessionUseCase(repo, student_repository=student_repo)
    return await use_case.execute(dto)


@router.get("/{session_id}", response_model=SessionResponseDTO)
async def get_session(session_id: str):
    repo = get_session_repository()
    use_case = GetSessionUseCase(repo)
    result = await use_case.execute(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.patch("/{session_id}", response_model=SessionResponseDTO)
async def update_session(session_id: str, dto: UpdateSessionDTO):
    repo = get_session_repository()
    use_case = UpdateSessionUseCase(repo)
    result = await use_case.execute(session_id, dto)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result
