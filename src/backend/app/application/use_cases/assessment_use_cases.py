from app.domain.entities.assessment import Assessment
from app.domain.interfaces.assessment_repository import AssessmentRepository
from app.application.dtos.assessment_dtos import (
    CreateAssessmentDTO,
    AssessmentResponseDTO,
)


class CreateAssessmentUseCase:
    def __init__(self, repository: AssessmentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateAssessmentDTO) -> AssessmentResponseDTO:
        assessment = Assessment(
            student_id=dto.student_id,
            session_id=dto.session_id,
            assessment_type=dto.assessment_type,
            score=dto.score,
            max_score=dto.max_score,
            responses=dto.responses,
            metadata=dto.metadata,
        )
        created = await self._repo.create(assessment)
        return _to_response(created)


class GetAssessmentUseCase:
    def __init__(self, repository: AssessmentRepository) -> None:
        self._repo = repository

    async def execute(self, assessment_id: str) -> AssessmentResponseDTO | None:
        assessment = await self._repo.get_by_id(assessment_id)
        if not assessment:
            return None
        return _to_response(assessment)


def _to_response(a: Assessment) -> AssessmentResponseDTO:
    return AssessmentResponseDTO(
        id=a.id,
        student_id=a.student_id,
        session_id=a.session_id,
        assessment_type=a.assessment_type,
        score=a.score,
        max_score=a.max_score,
        normalized_gain=a.normalized_gain,
        submitted_at=a.submitted_at.isoformat(),
        metadata=a.metadata,
    )
