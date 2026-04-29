"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter, HTTPException

from app.application.dtos.task_attempt_dtos import (
    CreateTaskAttemptDTO,
    TaskAttemptResponseDTO,
    UpdateTaskAttemptDTO,
)
from app.application.use_cases.task_attempt_use_cases import (
    CreateTaskAttemptUseCase,
    ListSessionTaskAttemptsUseCase,
    UpdateTaskAttemptUseCase,
)
from app.dependencies import get_task_attempt_repository

router = APIRouter()


@router.post("", response_model=TaskAttemptResponseDTO, status_code=201)
async def create_task_attempt(dto: CreateTaskAttemptDTO):
    repo = get_task_attempt_repository()
    use_case = CreateTaskAttemptUseCase(repo)
    return await use_case.execute(dto)


@router.patch("/{attempt_id}", response_model=TaskAttemptResponseDTO)
async def update_task_attempt(attempt_id: str, session_id: str, dto: UpdateTaskAttemptDTO):
    repo = get_task_attempt_repository()
    use_case = UpdateTaskAttemptUseCase(repo)
    try:
        return await use_case.execute(attempt_id, session_id, dto)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task attempt not found")


@router.get("/{session_id}", response_model=list[TaskAttemptResponseDTO])
async def list_session_task_attempts(session_id: str):
    repo = get_task_attempt_repository()
    use_case = ListSessionTaskAttemptsUseCase(repo)
    return await use_case.execute(session_id)
