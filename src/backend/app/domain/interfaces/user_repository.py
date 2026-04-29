"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: User repository port (DEC-024 vocabulary rename).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    """Port for user persistence."""

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_by_platform_identity(
        self, platform: str, platform_user_id: str
    ) -> User | None: ...

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[User]: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool: ...
