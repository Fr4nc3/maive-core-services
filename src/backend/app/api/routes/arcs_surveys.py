from fastapi import APIRouter

from app.application.dtos.arcs_survey_dtos import (
    ARCSSurveyResponseDTO,
    CreateARCSSurveyDTO,
)
from app.application.use_cases.arcs_survey_use_cases import (
    ListSessionARCSSurveysUseCase,
    SubmitARCSSurveyUseCase,
)
from app.dependencies import get_arcs_survey_repository

router = APIRouter()


@router.post("", response_model=ARCSSurveyResponseDTO, status_code=201)
async def submit_arcs_survey(dto: CreateARCSSurveyDTO):
    repo = get_arcs_survey_repository()
    use_case = SubmitARCSSurveyUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{session_id}", response_model=list[ARCSSurveyResponseDTO])
async def list_session_arcs_surveys(session_id: str):
    repo = get_arcs_survey_repository()
    use_case = ListSessionARCSSurveysUseCase(repo)
    return await use_case.execute(session_id)
