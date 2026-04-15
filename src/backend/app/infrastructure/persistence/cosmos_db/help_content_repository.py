from app.domain.entities.help_content import HelpContent
from app.domain.interfaces.help_content_repository import HelpContentRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)

_DT_FIELDS = ("created_at", "updated_at")


class CosmosHelpContentRepository(BaseCosmosRepository, HelpContentRepository):
    CONTAINER_NAME = "help_content"

    async def create(self, content: HelpContent) -> HelpContent:
        body = self._serialize_datetimes(content.model_dump(), _DT_FIELDS)
        self._container.create_item(body=body)
        return content

    async def update(self, content: HelpContent) -> HelpContent:
        body = self._serialize_datetimes(content.model_dump(), _DT_FIELDS)
        self._container.upsert_item(body=body)
        return content

    async def get_by_id(self, content_id: str, planet: str) -> HelpContent | None:
        try:
            item = self._container.read_item(
                item=content_id, partition_key=planet
            )
            return HelpContent.model_validate(self._strip_cosmos_meta(item))
        except Exception:
            return None

    async def query(
        self,
        planet: str,
        section: str | None = None,
        content_topic: str | None = None,
        difficulty_level: str | None = None,
        help_type: str | None = None,
        limit: int = 50,
    ) -> list[HelpContent]:
        conditions = ["c.planet = @planet", "c.is_active = true"]
        params: list[dict] = [{"name": "@planet", "value": planet}]

        if section:
            conditions.append("c.section = @section")
            params.append({"name": "@section", "value": section})
        if content_topic:
            conditions.append("c.content_topic = @content_topic")
            params.append({"name": "@content_topic", "value": content_topic})
        if difficulty_level:
            conditions.append("c.difficulty_level = @difficulty_level")
            params.append({"name": "@difficulty_level", "value": difficulty_level})
        if help_type:
            conditions.append("c.help_type = @help_type")
            params.append({"name": "@help_type", "value": help_type})

        params.append({"name": "@limit", "value": limit})
        query = (
            "SELECT TOP @limit * FROM c WHERE "
            + " AND ".join(conditions)
            + " ORDER BY c.display_order ASC"
        )
        items = list(
            self._container.query_items(
                query=query,
                parameters=params,
                partition_key=planet,
            )
        )
        return [HelpContent.model_validate(self._strip_cosmos_meta(i)) for i in items]

    async def list_planets(self) -> list[str]:
        query = "SELECT DISTINCT VALUE c.planet FROM c WHERE c.is_active = true"
        return list(
            self._container.query_items(
                query=query, enable_cross_partition_query=True
            )
        )
