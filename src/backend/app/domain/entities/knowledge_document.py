import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """Domain entity for NASA RAG knowledge chunks with vector embeddings."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    body_id: str  # partition key, e.g. "mars", "sun"
    body_name: str = ""  # display name, e.g. "Mars"
    source_url: str = ""
    title: str = ""
    content_text: str = ""
    content_type: str = ""  # "fact" | "explanation" | "procedure" | "quiz_context"
    section_tags: list[str] = Field(default_factory=list)
    topic_tags: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)
    chunk_index: int = 0
    total_chunks: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
