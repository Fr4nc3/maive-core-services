"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter

from app.application.dtos.qualitative_feedback_dtos import (
    CreateQualitativeFeedbackDTO,
    QualitativeFeedbackResponseDTO,
)
from app.application.use_cases.qualitative_feedback_use_cases import (
    ListSessionFeedbackUseCase,
    SubmitQualitativeFeedbackUseCase,
)
from app.dependencies import get_qualitative_feedback_repository

router = APIRouter()


@router.post("", response_model=QualitativeFeedbackResponseDTO, status_code=201)
async def submit_feedback(dto: CreateQualitativeFeedbackDTO):
    repo = get_qualitative_feedback_repository()
    use_case = SubmitQualitativeFeedbackUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{session_id}", response_model=list[QualitativeFeedbackResponseDTO])
async def list_session_feedback(session_id: str):
    repo = get_qualitative_feedback_repository()
    use_case = ListSessionFeedbackUseCase(repo)
    return await use_case.execute(session_id)
