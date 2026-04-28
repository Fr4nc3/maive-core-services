"""
CLI command to seed static HelpContent into Cosmos DB from JSON files.

Looks for files in:
  data/help_content/<planet>/*.json

Each JSON file may contain a single object or a list of objects matching
the HelpContent schema (planet, section, content_topic, difficulty_level,
help_type, title, body_text, ...).

Usage:
  uv run python -m app.cli.seed_help_content
  uv run python -m app.cli.seed_help_content --data-dir ../../data/help_content
  uv run python -m app.cli.seed_help_content --planet mars
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from app.config import settings
from app.domain.entities.help_content import HelpContent
from app.infrastructure.persistence.cosmos_db.client import get_cosmos_client
from app.infrastructure.persistence.cosmos_db.help_content_repository import (
    CosmosHelpContentRepository,
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


def _load_records(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Unsupported JSON root in {path}: expected dict or list")


async def main(data_dir: Path, planet_filter: str | None) -> None:
    if not data_dir.exists():
        logger.error("Help content directory not found: %s", data_dir)
        return

    client = get_cosmos_client()
    repo = CosmosHelpContentRepository(client, settings.cosmos_database)

    total = 0
    per_planet: dict[str, int] = {}

    planet_dirs = [p for p in data_dir.iterdir() if p.is_dir()]
    if planet_filter:
        planet_dirs = [p for p in planet_dirs if p.name == planet_filter]

    for planet_dir in planet_dirs:
        for json_file in sorted(planet_dir.glob("*.json")):
            try:
                records = _load_records(json_file)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("Skipping %s: %s", json_file, exc)
                continue

            for record in records:
                # Default planet from folder name if absent.
                record.setdefault("planet", planet_dir.name)
                entity = HelpContent(**record)
                await repo.create(entity)
                total += 1
                per_planet[entity.planet] = per_planet.get(entity.planet, 0) + 1

    logger.info("Seed complete: %d records loaded", total)
    for planet, count in per_planet.items():
        logger.info("  %s: %d", planet, count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed static HelpContent into Cosmos DB")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "data" / "help_content",
        help="Path to help_content directory (containing per-planet subfolders)",
    )
    parser.add_argument(
        "--planet",
        type=str,
        default=None,
        help="Optional: only seed a single planet folder",
    )
    args = parser.parse_args()
    asyncio.run(main(args.data_dir, args.planet))
