from app.application.dtos.classifier_prediction_dtos import (
    ClassifierPredictionResponseDTO,
    CreateClassifierPredictionDTO,
)
from app.domain.entities.classifier_prediction import ClassifierPrediction
from app.domain.interfaces.classifier_prediction_repository import (
    ClassifierPredictionRepository,
)


class CreateClassifierPredictionUseCase:
    def __init__(self, repository: ClassifierPredictionRepository) -> None:
        self._repo = repository

    async def execute(
        self, dto: CreateClassifierPredictionDTO
    ) -> ClassifierPredictionResponseDTO:
        prediction = ClassifierPrediction(
            session_id=dto.session_id,
            student_id=dto.student_id,
            model_version=dto.model_version,
            features_used=dto.features_used,
            predicted_probability=dto.predicted_probability,
            predicted_label=dto.predicted_label,
            actual_label=dto.actual_label,
            actual_score=dto.actual_score,
            confidence_interval=dto.confidence_interval,
        )
        created = await self._repo.create(prediction)
        return _to_response(created)


class GetSessionPredictionUseCase:
    def __init__(self, repository: ClassifierPredictionRepository) -> None:
        self._repo = repository

    async def execute(
        self, session_id: str
    ) -> ClassifierPredictionResponseDTO | None:
        prediction = await self._repo.get_by_session(session_id)
        return _to_response(prediction) if prediction else None


def _to_response(p: ClassifierPrediction) -> ClassifierPredictionResponseDTO:
    return ClassifierPredictionResponseDTO(
        id=p.id,
        session_id=p.session_id,
        student_id=p.student_id,
        model_version=p.model_version,
        features_used=p.features_used,
        predicted_probability=p.predicted_probability,
        predicted_label=p.predicted_label,
        actual_label=p.actual_label,
        actual_score=p.actual_score,
        confidence_interval=p.confidence_interval,
        created_at=p.created_at.isoformat(),
    )
