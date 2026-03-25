from azure.cosmos import CosmosClient

from app.domain.entities.classifier_prediction import ClassifierPrediction
from app.domain.interfaces.classifier_prediction_repository import (
    ClassifierPredictionRepository,
)


class CosmosClassifierPredictionRepository(ClassifierPredictionRepository):
    CONTAINER_NAME = "classifier_predictions"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, prediction: ClassifierPrediction) -> ClassifierPrediction:
        body = prediction.model_dump()
        body["created_at"] = body["created_at"].isoformat()
        self._container.create_item(body=body)
        return prediction

    async def get_by_session(self, session_id: str) -> ClassifierPrediction | None:
        query = "SELECT TOP 1 * FROM c WHERE c.session_id = @sid ORDER BY c.created_at DESC"
        parameters = [{"name": "@sid", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return ClassifierPrediction(**items[0]) if items else None

    async def list_by_student(self, student_id: str) -> list[ClassifierPrediction]:
        query = "SELECT * FROM c WHERE c.student_id = @sid ORDER BY c.created_at DESC"
        parameters = [{"name": "@sid", "value": student_id}]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        return [ClassifierPrediction(**item) for item in items]
