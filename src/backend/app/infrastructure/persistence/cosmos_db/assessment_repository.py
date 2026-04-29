"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from app.domain.entities.assessment import Assessment
from app.domain.interfaces.assessment_repository import AssessmentRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosAssessmentRepository(BaseCosmosRepository, AssessmentRepository):
    CONTAINER_NAME = "assessments"

    async def create(self, assessment: Assessment) -> Assessment:
        body = self._serialize_datetimes(assessment.model_dump(), ("submitted_at",))
        self._container.create_item(body=body)
        return assessment

    async def get_by_id(self, assessment_id: str) -> Assessment | None:
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": assessment_id}]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return Assessment(**items[0])

    async def list_by_student(
        self, student_id: str, limit: int = 50
    ) -> list[Assessment]:
        query = (
            "SELECT TOP @limit * FROM c"
            " WHERE c.student_id = @sid"
            " ORDER BY c.submitted_at DESC"
        )
        parameters = [
            {"name": "@sid", "value": student_id},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=student_id
            )
        )
        return [Assessment(**item) for item in items]
