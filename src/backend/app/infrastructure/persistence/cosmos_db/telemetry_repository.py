from azure.cosmos import CosmosClient

from app.domain.entities.telemetry import TelemetryEvent
from app.domain.interfaces.telemetry_repository import TelemetryRepository


class CosmosTelemetryRepository(TelemetryRepository):
    CONTAINER_NAME = "telemetry"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, event: TelemetryEvent) -> TelemetryEvent:
        body = event.model_dump()
        body["timestamp"] = body["timestamp"].isoformat()
        self._container.create_item(body=body)
        return event

    async def list_by_session(
        self, session_id: str, limit: int = 500
    ) -> list[TelemetryEvent]:
        query = "SELECT TOP @limit * FROM c WHERE c.session_id = @sid ORDER BY c.timestamp ASC"
        parameters = [
            {"name": "@sid", "value": session_id},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, partition_key=session_id
            )
        )
        return [TelemetryEvent(**item) for item in items]
