"""Admin endpoints for static help content (control arm).

Pillar: Scenario Pack
Phase: S
Purpose: Admin endpoints for static help content (control arm).
Documented in: data/help_content/README.md
"""

from fastapi import APIRouter, HTTPException

from app.application.dtos.help_content_dtos import (
    CreateHelpContentDTO,
    HelpContentResponseDTO,
    HelpQueryDTO,
    UpdateHelpContentDTO,
)
from app.application.use_cases.help_content_use_cases import (
    CreateHelpContentUseCase,
    GetHelpForContextUseCase,
    ListPlanetsUseCase,
    UpdateHelpContentUseCase,
)
from app.dependencies import get_help_content_repository

router = APIRouter()


@router.get("", response_model=list[HelpContentResponseDTO])
async def get_help(
    planet: str,
    section: str | None = None,
    content_topic: str | None = None,
    difficulty_level: str | None = None,
    help_type: str | None = None,
    limit: int = 50,
):
    """Fetch static help content for a given VR context."""
    repo = get_help_content_repository()
    query = HelpQueryDTO(
        planet=planet,
        section=section,
        content_topic=content_topic,
        difficulty_level=difficulty_level,
        help_type=help_type,
        limit=limit,
    )
    use_case = GetHelpForContextUseCase(repo)
    return await use_case.execute(query)


@router.get("/planets", response_model=list[str])
async def list_planets():
    """List all planets that have help content available."""
    repo = get_help_content_repository()
    use_case = ListPlanetsUseCase(repo)
    return await use_case.execute()


@router.post("", response_model=HelpContentResponseDTO, status_code=201)
async def create_help_content(dto: CreateHelpContentDTO):
    """Create a new static help content item."""
    repo = get_help_content_repository()
    use_case = CreateHelpContentUseCase(repo)
    return await use_case.execute(dto)


@router.patch("/{planet}/{content_id}", response_model=HelpContentResponseDTO)
async def update_help_content(
    planet: str, content_id: str, dto: UpdateHelpContentDTO
):
    """Update an existing help content item."""
    repo = get_help_content_repository()
    use_case = UpdateHelpContentUseCase(repo)
    result = await use_case.execute(content_id, planet, dto)
    if not result:
        raise HTTPException(status_code=404, detail="Help content not found")
    return result
