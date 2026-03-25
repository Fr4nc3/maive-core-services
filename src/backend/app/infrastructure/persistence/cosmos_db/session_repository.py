from azure.cosmos import CosmosClient, exceptions

from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import SessionRepository


class CosmosSessionRepository(SessionRepository):
    CONTAINER_NAME = "sessions"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, session: Session) -> Session:
        body = session.model_dump()
        body["ended_at"] = body["ended_at"].isoformat() if body["ended_at"] else None
        body["started_at"] = body["started_at"].isoformat()
        self._container.create_item(body=body)
        return session

    async def get_by_id(self, session_id: str) -> Session | None:
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": session_id}]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        if not items:
            return None
        return Session(**items[0])

    async def list_by_student(
        self, student_id: str, limit: int = 50
    ) -> list[Session]:
        query = "SELECT TOP @limit * FROM c WHERE c.student_id = @sid ORDER BY c.started_at DESC"
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
        body = session.model_dump()
        body["ended_at"] = body["ended_at"].isoformat() if body["ended_at"] else None
        body["started_at"] = body["started_at"].isoformat()
        self._container.upsert_item(body=body)
        return session
