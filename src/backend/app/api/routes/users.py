"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter, HTTPException

from app.application.dtos.user_dtos import (
    CreateUserDTO,
    IdentifyUserDTO,
    UserResponseDTO,
)
from app.application.use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    IdentifyOrCreateUserUseCase,
    ListUsersUseCase,
)
from app.dependencies import get_user_repository

router = APIRouter()


@router.post("/identify", response_model=UserResponseDTO)
async def identify_user(dto: IdentifyUserDTO):
    """Idempotent client identity endpoint.

    Every VR/web client calls this on first interaction. Returns the existing
    user for ``(platform, platform_user_id)`` or creates a new one. The
    returned ``id`` (UUID) is the stable internal identifier the client must
    reuse for all subsequent calls.
    """
    repo = get_user_repository()
    use_case = IdentifyOrCreateUserUseCase(repo)
    return await use_case.execute(dto)


@router.post("", response_model=UserResponseDTO, status_code=201)
async def create_user(dto: CreateUserDTO):
    repo = get_user_repository()
    use_case = CreateUserUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(user_id: str):
    repo = get_user_repository()
    use_case = GetUserUseCase(repo)
    result = await use_case.execute(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("", response_model=list[UserResponseDTO])
async def list_users(limit: int = 50, offset: int = 0):
    repo = get_user_repository()
    use_case = ListUsersUseCase(repo)
    return await use_case.execute(limit=limit, offset=offset)
