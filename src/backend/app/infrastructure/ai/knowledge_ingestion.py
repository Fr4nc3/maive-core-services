"""
Knowledge ingestion pipeline.

Loads NASA markdown files, chunks them, generates embeddings,
and stores them in Cosmos DB for RAG vector search.

Pillar: Stable Core
Phase: D
Purpose: NASA RAG ingestion (chunk -> embed -> store).
Documented in: docs/knowledge-ingestion.md
"""

import logging
from pathlib import Path

from app.domain.entities.knowledge_document import KnowledgeDocument
from app.domain.interfaces.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.ai.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Mapping from filename stem to display name
BODY_NAMES: dict[str, str] = {
    "sun": "Sun",
    "mercury": "Mercury",
    "venus": "Venus",
    "earth": "Earth",
    "moon": "Moon",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
}


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


def parse_sections(text: str) -> list[dict[str, str]]:
    """Parse markdown into sections based on headings."""
    sections: list[dict[str, str]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("# ") or line.startswith("## "):
            if current_lines:
                sections.append({
                    "title": current_title,
                    "text": "\n".join(current_lines).strip(),
                })
            current_title = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "title": current_title,
            "text": "\n".join(current_lines).strip(),
        })

    return [s for s in sections if s["text"]]


async def ingest_file(
    file_path: Path,
    embedding_service: EmbeddingService,
    repository: KnowledgeDocumentRepository,
    source_url: str = "",
) -> int:
    """Ingest a single NASA markdown file into the knowledge store."""
    body_id = file_path.stem.lower()
    body_name = BODY_NAMES.get(body_id, body_id.title())

    logger.info("Ingesting %s (%s) from %s", body_name, body_id, file_path)

    text = file_path.read_text(encoding="utf-8")
    sections = parse_sections(text)

    all_chunks: list[dict] = []
    for section in sections:
        chunks = chunk_text(section["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "title": section["title"],
                "text": chunk,
                "chunk_index": len(all_chunks),
            })

    total_chunks = len(all_chunks)
    if total_chunks == 0:
        logger.warning("No content found in %s", file_path)
        return 0

    # Batch embed all chunks
    texts = [c["text"] for c in all_chunks]
    embeddings = await embedding_service.embed_batch(texts)

    # Store each chunk
    count = 0
    for chunk_data, embedding in zip(all_chunks, embeddings):
        doc = KnowledgeDocument(
            body_id=body_id,
            body_name=body_name,
            source_url=source_url,
            title=chunk_data["title"],
            content_text=chunk_data["text"],
            content_type="fact",
            section_tags=[chunk_data["title"].lower().replace(" ", "-")],
            topic_tags=[body_id],
            embedding=embedding,
            chunk_index=chunk_data["chunk_index"],
            total_chunks=total_chunks,
        )
        await repository.create(doc)
        count += 1

    logger.info("Stored %d chunks for %s", count, body_name)
    return count


async def ingest_directory(
    data_dir: Path,
    embedding_service: EmbeddingService,
    repository: KnowledgeDocumentRepository,
) -> dict[str, int]:
    """Ingest all .md files from a directory."""
    results: dict[str, int] = {}
    for md_file in sorted(data_dir.glob("*.md")):
        count = await ingest_file(md_file, embedding_service, repository)
        results[md_file.stem] = count
    return results
