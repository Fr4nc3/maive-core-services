"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from app.domain.entities.qualitative_feedback import QualitativeFeedback
from app.domain.interfaces.qualitative_feedback_repository import (
    QualitativeFeedbackRepository,
)
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosQualitativeFeedbackRepository(
    BaseCosmosRepository, QualitativeFeedbackRepository
):
    CONTAINER_NAME = "qualitative_feedback"

    async def create(self, feedback: QualitativeFeedback) -> QualitativeFeedback:
        body = self._serialize_datetimes(feedback.model_dump(), ("submitted_at",))
        self._container.create_item(body=body)
        return feedback

    async def list_by_session(self, session_id: str) -> list[QualitativeFeedback]:
        query = (
            "SELECT * FROM c WHERE c.session_id = @sid"
            " ORDER BY c.submitted_at ASC"
        )
        parameters = [{"name": "@sid", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return [QualitativeFeedback(**item) for item in items]
