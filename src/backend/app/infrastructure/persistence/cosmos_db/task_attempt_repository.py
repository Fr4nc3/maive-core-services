from azure.cosmos import CosmosClient

from app.domain.entities.task_attempt import TaskAttempt
from app.domain.interfaces.task_attempt_repository import TaskAttemptRepository


class CosmosTaskAttemptRepository(TaskAttemptRepository):
    CONTAINER_NAME = "task_attempts"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, attempt: TaskAttempt) -> TaskAttempt:
        body = attempt.model_dump()
        body["started_at"] = body["started_at"].isoformat()
        if body.get("completed_at"):
            body["completed_at"] = body["completed_at"].isoformat()
        self._container.create_item(body=body)
        return attempt

    async def update(self, attempt: TaskAttempt) -> TaskAttempt:
        body = attempt.model_dump()
        body["started_at"] = body["started_at"].isoformat()
        if body.get("completed_at"):
            body["completed_at"] = body["completed_at"].isoformat()
        self._container.upsert_item(body=body)
        return attempt

    async def get_by_id(self, attempt_id: str, session_id: str) -> TaskAttempt | None:
        try:
            item = self._container.read_item(item=attempt_id, partition_key=session_id)
            return TaskAttempt(**item)
        except Exception:
            return None

    async def list_by_session(self, session_id: str) -> list[TaskAttempt]:
        query = "SELECT * FROM c WHERE c.session_id = @sid ORDER BY c.started_at ASC"
        parameters = [{"name": "@sid", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return [TaskAttempt(**item) for item in items]
