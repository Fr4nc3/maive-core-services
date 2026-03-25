from fastapi import APIRouter, HTTPException

from app.application.dtos.classifier_prediction_dtos import (
    CreateClassifierPredictionDTO,
    ClassifierPredictionResponseDTO,
)
from app.application.use_cases.classifier_prediction_use_cases import (
    CreateClassifierPredictionUseCase,
    GetSessionPredictionUseCase,
)
from app.dependencies import get_classifier_prediction_repository

router = APIRouter()


@router.post("", response_model=ClassifierPredictionResponseDTO, status_code=201)
async def create_prediction(dto: CreateClassifierPredictionDTO):
    repo = get_classifier_prediction_repository()
    use_case = CreateClassifierPredictionUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{session_id}", response_model=ClassifierPredictionResponseDTO)
async def get_session_prediction(session_id: str):
    repo = get_classifier_prediction_repository()
    use_case = GetSessionPredictionUseCase(repo)
    result = await use_case.execute(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="No prediction for this session")
    return result
