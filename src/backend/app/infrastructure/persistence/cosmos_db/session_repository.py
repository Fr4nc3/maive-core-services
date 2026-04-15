from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import SessionRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)

_DT_FIELDS = ("started_at", "ended_at")


class CosmosSessionRepository(BaseCosmosRepository, SessionRepository):
    CONTAINER_NAME = "sessions"

    async def create(self, session: Session) -> Session:
        body = self._serialize_datetimes(session.model_dump(), _DT_FIELDS)
        self._container.create_item(body=body)
        return session

    async def get_by_id(self, session_id: str) -> Session | None:
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return Session(**items[0])

    async def list_by_student(
        self, student_id: str, limit: int = 50
    ) -> list[Session]:
        query = (
            "SELECT TOP @limit * FROM c"
            " WHERE c.student_id = @sid"
            " ORDER BY c.started_at DESC"
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
        return [Session(**item) for item in items]

    async def update(self, session: Session) -> Session:
        body = self._serialize_datetimes(session.model_dump(), _DT_FIELDS)
        self._container.upsert_item(body=body)
        return session
