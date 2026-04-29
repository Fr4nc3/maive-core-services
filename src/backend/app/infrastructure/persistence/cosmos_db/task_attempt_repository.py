"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from app.domain.entities.task_attempt import TaskAttempt
from app.domain.interfaces.task_attempt_repository import TaskAttemptRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)

_DT_FIELDS = ("started_at", "completed_at")


class CosmosTaskAttemptRepository(BaseCosmosRepository, TaskAttemptRepository):
    CONTAINER_NAME = "task_attempts"

    async def create(self, attempt: TaskAttempt) -> TaskAttempt:
        body = self._serialize_datetimes(attempt.model_dump(), _DT_FIELDS)
        self._container.create_item(body=body)
        return attempt

    async def update(self, attempt: TaskAttempt) -> TaskAttempt:
        body = self._serialize_datetimes(attempt.model_dump(), _DT_FIELDS)
        self._container.upsert_item(body=body)
        return attempt

    async def get_by_id(self, attempt_id: str, session_id: str) -> TaskAttempt | None:
        try:
            item = self._container.read_item(
                item=attempt_id, partition_key=session_id
            )
            return TaskAttempt(**self._strip_cosmos_meta(item))
        except Exception:
            return None

    async def list_by_session(self, session_id: str) -> list[TaskAttempt]:
        query = (
            "SELECT * FROM c WHERE c.session_id = @sid"
            " ORDER BY c.started_at ASC"
        )
        parameters = [{"name": "@sid", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return [TaskAttempt(**item) for item in items]
