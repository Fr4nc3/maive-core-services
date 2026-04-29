"""Use case orchestrating domain + repository ports.

Pillar: Stable Core
Phase: B
Purpose: Use case orchestrating domain + repository ports.
Documented in: plan/architecture.md
"""

from app.application.dtos.arcs_survey_dtos import (
    ARCSSurveyResponseDTO,
    CreateARCSSurveyDTO,
)
from app.domain.entities.arcs_survey import ARCSSurveyResponse
from app.domain.interfaces.arcs_survey_repository import ARCSSurveyRepository


class SubmitARCSSurveyUseCase:
    def __init__(self, repository: ARCSSurveyRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateARCSSurveyDTO) -> ARCSSurveyResponseDTO:
        composite = (
            dto.attention_score
            + dto.relevance_score
            + dto.confidence_score
            + dto.satisfaction_score
        ) / 4.0
        response = ARCSSurveyResponse(
            session_id=dto.session_id,
            user_id=dto.user_id,
            module_id=dto.module_id,
            attention_score=dto.attention_score,
            relevance_score=dto.relevance_score,
            confidence_score=dto.confidence_score,
            satisfaction_score=dto.satisfaction_score,
            composite_score=composite,
            item_responses=dto.item_responses,
            completion_time_ms=dto.completion_time_ms,
        )
        created = await self._repo.create(response)
        return _to_response(created)


class ListSessionARCSSurveysUseCase:
    def __init__(self, repository: ARCSSurveyRepository) -> None:
        self._repo = repository

    async def execute(self, session_id: str) -> list[ARCSSurveyResponseDTO]:
        surveys = await self._repo.list_by_session(session_id)
        return [_to_response(s) for s in surveys]


def _to_response(s: ARCSSurveyResponse) -> ARCSSurveyResponseDTO:
    return ARCSSurveyResponseDTO(
        id=s.id,
        session_id=s.session_id,
        user_id=s.user_id,
        module_id=s.module_id,
        attention_score=s.attention_score,
        relevance_score=s.relevance_score,
        confidence_score=s.confidence_score,
        satisfaction_score=s.satisfaction_score,
        composite_score=s.composite_score,
        item_responses=s.item_responses,
        completion_time_ms=s.completion_time_ms,
        submitted_at=s.submitted_at.isoformat(),
    )
