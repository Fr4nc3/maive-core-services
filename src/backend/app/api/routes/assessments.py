"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter, HTTPException

from app.application.dtos.assessment_dtos import (
    AssessmentResponseDTO,
    CreateAssessmentDTO,
)
from app.application.use_cases.assessment_use_cases import (
    CreateAssessmentUseCase,
    GetAssessmentUseCase,
)
from app.dependencies import get_assessment_repository

router = APIRouter()


@router.post("", response_model=AssessmentResponseDTO, status_code=201)
async def create_assessment(dto: CreateAssessmentDTO):
    repo = get_assessment_repository()
    use_case = CreateAssessmentUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{assessment_id}", response_model=AssessmentResponseDTO)
async def get_assessment(assessment_id: str):
    repo = get_assessment_repository()
    use_case = GetAssessmentUseCase(repo)
    result = await use_case.execute(assessment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result
