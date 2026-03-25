import logging

from azure.cosmos import CosmosClient
from app.config import settings

logger = logging.getLogger(__name__)

_client: CosmosClient | None = None


def get_cosmos_client() -> CosmosClient:
    """Return a singleton Cosmos DB client instance."""
    global _client
    if _client is None:
        logger.info("Initializing Cosmos DB client — endpoint=%s", settings.cosmos_endpoint)
        _client = CosmosClient(
            url=settings.cosmos_endpoint,
            credential=settings.cosmos_key,
        )
    return _client
