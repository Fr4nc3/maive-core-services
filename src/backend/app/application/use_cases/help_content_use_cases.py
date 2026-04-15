from datetime import datetime

from app.application.dtos.help_content_dtos import (
    CreateHelpContentDTO,
    HelpContentResponseDTO,
    HelpQueryDTO,
    UpdateHelpContentDTO,
)
from app.domain.entities.help_content import HelpContent
from app.domain.interfaces.help_content_repository import HelpContentRepository


class GetHelpForContextUseCase:
    """Returns static help content matching planet/section/topic context."""

    def __init__(self, repository: HelpContentRepository) -> None:
        self._repo = repository

    async def execute(self, query: HelpQueryDTO) -> list[HelpContentResponseDTO]:
        items = await self._repo.query(
            planet=query.planet,
            section=query.section,
            content_topic=query.content_topic,
            difficulty_level=query.difficulty_level,
            help_type=query.help_type,
            limit=query.limit,
        )
        return [_to_response(h) for h in items]


class CreateHelpContentUseCase:
    def __init__(self, repository: HelpContentRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateHelpContentDTO) -> HelpContentResponseDTO:
        content = HelpContent(
            planet=dto.planet,
            section=dto.section,
            content_topic=dto.content_topic,
            difficulty_level=dto.difficulty_level,
            help_type=dto.help_type,
            title=dto.title,
            body_text=dto.body_text,
            media_url=dto.media_url,
            display_order=dto.display_order,
            tags=dto.tags,
            is_active=dto.is_active,
        )
        created = await self._repo.create(content)
        return _to_response(created)


class UpdateHelpContentUseCase:
    def __init__(self, repository: HelpContentRepository) -> None:
        self._repo = repository

    async def execute(
        self, content_id: str, planet: str, dto: UpdateHelpContentDTO
    ) -> HelpContentResponseDTO | None:
        content = await self._repo.get_by_id(content_id, planet)
        if not content:
            return None
        update_data = dto.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(content, key, value)
        content.updated_at = datetime.utcnow()
        updated = await self._repo.update(content)
        return _to_response(updated)


class ListPlanetsUseCase:
    def __init__(self, repository: HelpContentRepository) -> None:
        self._repo = repository

    async def execute(self) -> list[str]:
        return await self._repo.list_planets()


def _to_response(h: HelpContent) -> HelpContentResponseDTO:
    return HelpContentResponseDTO(
        id=h.id,
        planet=h.planet,
        section=h.section,
        content_topic=h.content_topic,
        difficulty_level=h.difficulty_level,
        help_type=h.help_type,
        title=h.title,
        body_text=h.body_text,
        media_url=h.media_url,
        display_order=h.display_order,
        tags=h.tags,
        is_active=h.is_active,
    )
