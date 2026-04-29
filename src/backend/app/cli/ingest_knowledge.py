"""
CLI command to ingest NASA knowledge data into Cosmos DB with embeddings.

Usage:
  uv run python -m app.cli.ingest_knowledge
  uv run python -m app.cli.ingest_knowledge --data-dir ../../data/nasa
  uv run python -m app.cli.ingest_knowledge --provider ollama
  uv run python -m app.cli.ingest_knowledge --provider azure

Pillar: Configuration Layer
Phase: D
Purpose: CLI for NASA RAG ingestion.
Documented in: docs/knowledge-ingestion.md
"""

import argparse
import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.dependencies import build_llm_provider
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.ai.knowledge_ingestion import ingest_directory

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


async def main(data_dir: Path, provider_name: str) -> None:
    from app.infrastructure.persistence.cosmos_db.client import get_cosmos_client
    from app.infrastructure.persistence.cosmos_db.knowledge_document_repository import (
        CosmosKnowledgeDocumentRepository,
    )

    if not data_dir.exists():
        logger.error("Data directory not found: %s", data_dir)
        return

    # Temporarily override provider setting if specified via CLI
    settings.llm_provider = provider_name
    provider = build_llm_provider()
    embedding_service = EmbeddingService(provider)

    client = get_cosmos_client()
    repository = CosmosKnowledgeDocumentRepository(client, settings.cosmos_database)

    logger.info("Starting ingestion from %s using %s provider", data_dir, provider_name)
    results = await ingest_directory(data_dir, embedding_service, repository)

    total = sum(results.values())
    logger.info("Ingestion complete: %d total chunks across %d bodies", total, len(results))
    for body, count in results.items():
        logger.info("  %s: %d chunks", body, count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest NASA knowledge data")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "data" / "nasa",
        help="Path to NASA markdown files",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "azure"],
        default=settings.llm_provider,
        help="LLM provider for embeddings",
    )
    args = parser.parse_args()
    asyncio.run(main(args.data_dir, args.provider))
