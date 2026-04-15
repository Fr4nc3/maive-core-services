from app.domain.entities.agent_action import AgentAction
from app.domain.interfaces.agent_action_repository import AgentActionRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosAgentActionRepository(BaseCosmosRepository, AgentActionRepository):
    CONTAINER_NAME = "agent_actions"

    async def create(self, action: AgentAction) -> AgentAction:
        body = self._serialize_datetimes(action.model_dump(), ("triggered_at",))
        self._container.create_item(body=body)
        return action

    async def get_by_id(
        self, action_id: str, session_id: str
    ) -> AgentAction | None:
        try:
            item = self._container.read_item(
                item=action_id, partition_key=session_id
            )
            return AgentAction.model_validate(self._strip_cosmos_meta(item))
        except Exception:
            return None

    async def list_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[AgentAction]:
        query = (
            "SELECT TOP @limit * FROM c WHERE c.session_id = @sid"
            " ORDER BY c.triggered_at DESC"
        )
        params = [
            {"name": "@sid", "value": session_id},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(
                query=query,
                parameters=params,
                partition_key=session_id,
            )
        )
        return [AgentAction.model_validate(self._strip_cosmos_meta(i)) for i in items]
