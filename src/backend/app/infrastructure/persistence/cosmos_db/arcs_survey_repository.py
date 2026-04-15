from app.domain.entities.arcs_survey import ARCSSurveyResponse
from app.domain.interfaces.arcs_survey_repository import ARCSSurveyRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosARCSSurveyRepository(BaseCosmosRepository, ARCSSurveyRepository):
    CONTAINER_NAME = "arcs_surveys"

    async def create(self, response: ARCSSurveyResponse) -> ARCSSurveyResponse:
        body = self._serialize_datetimes(response.model_dump(), ("submitted_at",))
        self._container.create_item(body=body)
        return response

    async def list_by_session(self, session_id: str) -> list[ARCSSurveyResponse]:
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
        return [ARCSSurveyResponse(**item) for item in items]

    async def list_by_student(self, student_id: str) -> list[ARCSSurveyResponse]:
        query = (
            "SELECT * FROM c WHERE c.student_id = @sid"
            " ORDER BY c.submitted_at ASC"
        )
        parameters = [{"name": "@sid", "value": student_id}]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        return [ARCSSurveyResponse(**item) for item in items]
