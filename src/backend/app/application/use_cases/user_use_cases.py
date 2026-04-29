"""Use case orchestrating domain + repository ports.

Pillar: Stable Core
Phase: B
Purpose: Use case orchestrating domain + repository ports.
Documented in: plan/architecture.md
"""

from app.application.dtos.user_dtos import (
    CreateUserDTO,
    IdentifyUserDTO,
    UserResponseDTO,
)
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import UserRepository


class IdentifyOrCreateUserUseCase:
    """Idempotent: returns the existing user for ``(platform, platform_user_id)``
    or creates one if absent. This is the entry point every VR/web client calls
    on first interaction.
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def execute(self, dto: IdentifyUserDTO) -> UserResponseDTO:
        existing = await self._repo.get_by_platform_identity(
            dto.platform, dto.platform_user_id
        )
        if existing is not None:
            return _to_response(existing)
        user = User(
            platform=dto.platform,
            platform_user_id=dto.platform_user_id,
            display_name=dto.display_name,
            preferred_language=dto.preferred_language,
            metadata=dto.metadata,
        )
        created = await self._repo.create(user)
        return _to_response(created)


class CreateUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        user = User(
            platform=dto.platform,
            platform_user_id=dto.platform_user_id,
            display_name=dto.display_name,
            preferred_language=dto.preferred_language,
            metadata=dto.metadata,
        )
        created = await self._repo.create(user)
        return _to_response(created)


class GetUserUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def execute(self, user_id: str) -> UserResponseDTO | None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            return None
        return _to_response(user)


class ListUsersUseCase:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def execute(
        self, limit: int = 50, offset: int = 0
    ) -> list[UserResponseDTO]:
        users = await self._repo.list_all(limit=limit, offset=offset)
        return [_to_response(s) for s in users]


def _to_response(s: User) -> UserResponseDTO:
    return UserResponseDTO(
        id=s.id,
        platform=s.platform,
        platform_user_id=s.platform_user_id,
        display_name=s.display_name,
        preferred_language=s.preferred_language,
        created_at=s.created_at.isoformat(),
        metadata=s.metadata,
    )
