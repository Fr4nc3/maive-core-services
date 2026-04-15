"""
Base Cosmos DB repository with shared boilerplate.
"""

from azure.cosmos import CosmosClient

# Cosmos DB metadata keys to strip from query results
_COSMOS_META_KEYS = ("_rid", "_self", "_etag", "_attachments", "_ts")


class BaseCosmosRepository:
    """Shared init + helpers for all Cosmos DB repositories."""

    CONTAINER_NAME: str = ""  # Override in subclass

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    @staticmethod
    def _strip_cosmos_meta(item: dict, extra_keys: tuple[str, ...] = ()) -> dict:
        """Remove Cosmos DB internal metadata from a raw item dict."""
        for key in _COSMOS_META_KEYS + extra_keys:
            item.pop(key, None)
        return item

    @staticmethod
    def _serialize_datetimes(data: dict, fields: tuple[str, ...]) -> dict:
        """Convert datetime fields to ISO-format strings for Cosmos DB storage."""
        for field in fields:
            val = data.get(field)
            if val is not None and hasattr(val, "isoformat"):
                data[field] = val.isoformat()
        return data
