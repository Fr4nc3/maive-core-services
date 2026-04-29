"""Module under MAIVE Clean Architecture.

Pillar: Stable Core
Phase: B
Purpose: Module under MAIVE Clean Architecture.
Documented in: plan/architecture.md
"""

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import UserRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosUserRepository(BaseCosmosRepository, UserRepository):
    CONTAINER_NAME = "users"

    async def create(self, user: User) -> User:
        self._container.create_item(body=user.model_dump())
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            item = self._container.read_item(item=user_id, partition_key=user_id)
            return User(**self._strip_cosmos_meta(item))
        except CosmosResourceNotFoundError:
            return None

    async def get_by_platform_identity(
        self, platform: str, platform_user_id: str
    ) -> User | None:
        query = (
            "SELECT TOP 1 * FROM c WHERE c.platform = @p AND c.platform_user_id = @uid"
        )
        parameters = [
            {"name": "@p", "value": platform},
            {"name": "@uid", "value": platform_user_id},
        ]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return User(**self._strip_cosmos_meta(items[0]))

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[User]:
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
        parameters = [
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        return [User(**item) for item in items]

    async def update(self, user: User) -> User:
        self._container.upsert_item(body=user.model_dump())
        return user

    async def delete(self, user_id: str) -> bool:
        try:
            self._container.delete_item(item=user_id, partition_key=user_id)
            return True
        except CosmosResourceNotFoundError:
            return False
