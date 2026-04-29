"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from app.domain.entities.telemetry import TelemetryEvent
from app.domain.interfaces.telemetry_repository import TelemetryRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosTelemetryRepository(BaseCosmosRepository, TelemetryRepository):
    CONTAINER_NAME = "telemetry"

    async def create(self, event: TelemetryEvent) -> TelemetryEvent:
        body = self._serialize_datetimes(event.model_dump(), ("timestamp",))
        self._container.create_item(body=body)
        return event

    async def list_by_session(
        self, session_id: str, limit: int = 500
    ) -> list[TelemetryEvent]:
        query = (
            "SELECT TOP @limit * FROM c"
            " WHERE c.session_id = @sid"
            " ORDER BY c.timestamp ASC"
        )
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
