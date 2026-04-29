"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from app.domain.entities.knowledge_document import KnowledgeDocument
from app.domain.interfaces.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosKnowledgeDocumentRepository(
    BaseCosmosRepository, KnowledgeDocumentRepository
):
    CONTAINER_NAME = "knowledge_documents"

    async def create(self, doc: KnowledgeDocument) -> KnowledgeDocument:
        body = self._serialize_datetimes(doc.model_dump(), ("created_at",))
        self._container.create_item(body=body)
        return doc

    async def vector_search(
        self,
        embedding: list[float],
        body_id: str | None = None,
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        query = (
            "SELECT TOP @limit c.id, c.body_id, c.body_name, c.source_url,"
            " c.title, c.content_text, c.content_type, c.section_tags,"
            " c.topic_tags, c.chunk_index, c.total_chunks, c.created_at,"
            " VectorDistance(c.embedding, @embedding) AS score"
            " FROM c"
        )
        params: list[dict] = [
            {"name": "@embedding", "value": embedding},
            {"name": "@limit", "value": limit},
        ]

        if body_id:
            query += " WHERE c.body_id = @body_id"
            params.append({"name": "@body_id", "value": body_id})

        query += " ORDER BY VectorDistance(c.embedding, @embedding)"

        items = list(
            self._container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=body_id is None,
                partition_key=body_id if body_id else None,
            )
        )
        return [
            KnowledgeDocument.model_validate(
                self._strip_cosmos_meta(i, extra_keys=("score", "embedding"))
            )
            for i in items
        ]

    async def list_by_body(self, body_id: str) -> list[KnowledgeDocument]:
        query = (
            "SELECT * FROM c WHERE c.body_id = @body_id"
            " ORDER BY c.chunk_index ASC"
        )
        items = list(
            self._container.query_items(
                query=query,
                parameters=[{"name": "@body_id", "value": body_id}],
                partition_key=body_id,
            )
        )
        return [
            KnowledgeDocument.model_validate(
                self._strip_cosmos_meta(i, extra_keys=("embedding",))
            )
            for i in items
        ]
