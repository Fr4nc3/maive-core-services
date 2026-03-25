from azure.cosmos import CosmosClient

from app.domain.entities.qualitative_feedback import QualitativeFeedback
from app.domain.interfaces.qualitative_feedback_repository import (
    QualitativeFeedbackRepository,
)


class CosmosQualitativeFeedbackRepository(QualitativeFeedbackRepository):
    CONTAINER_NAME = "qualitative_feedback"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, feedback: QualitativeFeedback) -> QualitativeFeedback:
        body = feedback.model_dump()
        body["submitted_at"] = body["submitted_at"].isoformat()
        self._container.create_item(body=body)
        return feedback

    async def list_by_session(self, session_id: str) -> list[QualitativeFeedback]:
        query = "SELECT * FROM c WHERE c.session_id = @sid ORDER BY c.submitted_at ASC"
        parameters = [{"name": "@sid", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return [QualitativeFeedback(**item) for item in items]
