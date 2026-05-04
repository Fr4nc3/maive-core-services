"""Cosmos client (passwordless via Managed Identity, DEC-021).

Pillar: Stable Core
Phase: Q
Purpose: Cosmos client (passwordless via Managed Identity, DEC-021).
Documented in: docs/deployment/runbook.md
"""

import logging

from azure.cosmos import CosmosClient

from app.config import settings
from app.infrastructure.azure.credentials import get_azure_credential

logger = logging.getLogger(__name__)

_client: CosmosClient | None = None


def get_cosmos_client() -> CosmosClient:
    """Return a singleton Cosmos DB client instance."""
    global _client
    if _client is None:
        logger.info("Initializing Cosmos DB client - endpoint=%s", settings.cosmos_endpoint)
        _client = CosmosClient(
            url=settings.cosmos_endpoint,
            credential=get_azure_credential(),
        )
    return _client
