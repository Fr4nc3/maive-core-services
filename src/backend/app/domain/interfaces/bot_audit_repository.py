"""Append-only audit repository port.

Pillar: Stable Core
Phase: R
Purpose: Append-only audit repository port.
Documented in: docs/rai-policy.md#bot_audit
"""

from abc import ABC, abstractmethod

from app.domain.entities.bot_audit import BotAudit


class BotAuditRepository(ABC):
    """Port for bot_audit persistence.

    Append-only by design (DEC-013). No update / no delete.
    """

    @abstractmethod
    async def create(self, audit: BotAudit) -> BotAudit: ...

    @abstractmethod
    async def list_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[BotAudit]: ...
