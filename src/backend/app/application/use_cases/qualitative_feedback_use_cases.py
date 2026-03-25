from app.domain.entities.qualitative_feedback import QualitativeFeedback
from app.domain.interfaces.qualitative_feedback_repository import (
    QualitativeFeedbackRepository,
)
from app.application.dtos.qualitative_feedback_dtos import (
    CreateQualitativeFeedbackDTO,
    QualitativeFeedbackResponseDTO,
)


class SubmitQualitativeFeedbackUseCase:
    def __init__(self, repository: QualitativeFeedbackRepository) -> None:
        self._repo = repository

    async def execute(
        self, dto: CreateQualitativeFeedbackDTO
    ) -> QualitativeFeedbackResponseDTO:
        feedback = QualitativeFeedback(
            session_id=dto.session_id,
            student_id=dto.student_id,
            prompt=dto.prompt,
            arcs_dimension=dto.arcs_dimension,
            response_text=dto.response_text,
        )
        created = await self._repo.create(feedback)
        return _to_response(created)


class ListSessionFeedbackUseCase:
    def __init__(self, repository: QualitativeFeedbackRepository) -> None:
        self._repo = repository

    async def execute(
        self, session_id: str
    ) -> list[QualitativeFeedbackResponseDTO]:
        items = await self._repo.list_by_session(session_id)
        return [_to_response(f) for f in items]


def _to_response(f: QualitativeFeedback) -> QualitativeFeedbackResponseDTO:
    return QualitativeFeedbackResponseDTO(
        id=f.id,
        session_id=f.session_id,
        student_id=f.student_id,
        prompt=f.prompt,
        arcs_dimension=f.arcs_dimension,
        response_text=f.response_text,
        submitted_at=f.submitted_at.isoformat(),
        theme_codes=f.theme_codes,
    )
