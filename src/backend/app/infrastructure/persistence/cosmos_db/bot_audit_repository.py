"""Cosmos DB implementation of BotAuditRepository (append-only).

Pillar: Stable Core
Phase: R
Purpose: Cosmos impl of append-only bot_audit (PK /session_id).
Documented in: docs/rai-policy.md#bot_audit
"""

from app.domain.entities.bot_audit import BotAudit
from app.domain.interfaces.bot_audit_repository import BotAuditRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)

_DT_FIELDS = ("request_ts", "response_ts")


class CosmosBotAuditRepository(BaseCosmosRepository, BotAuditRepository):
    CONTAINER_NAME = "bot_audit"

    async def create(self, audit: BotAudit) -> BotAudit:
        body = self._serialize_datetimes(audit.model_dump(), _DT_FIELDS)
        self._container.create_item(body=body)
        return audit

    async def list_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[BotAudit]:
        query = (
            "SELECT TOP @limit * FROM c"
            " WHERE c.session_id = @sid"
            " ORDER BY c.request_ts DESC"
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
        return [BotAudit(**self._strip_cosmos_meta(item)) for item in items]
