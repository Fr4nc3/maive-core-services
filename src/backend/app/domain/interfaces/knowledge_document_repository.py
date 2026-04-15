from abc import ABC, abstractmethod

from app.domain.entities.knowledge_document import KnowledgeDocument


class KnowledgeDocumentRepository(ABC):
    """Port for NASA knowledge document persistence with vector search."""

    @abstractmethod
    async def create(self, doc: KnowledgeDocument) -> KnowledgeDocument: ...

    @abstractmethod
    async def vector_search(
        self,
        embedding: list[float],
        body_id: str | None = None,
        limit: int = 5,
    ) -> list[KnowledgeDocument]: ...

    @abstractmethod
    async def list_by_body(self, body_id: str) -> list[KnowledgeDocument]: ...
