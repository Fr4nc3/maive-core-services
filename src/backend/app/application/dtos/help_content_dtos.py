from pydantic import BaseModel


class CreateHelpContentDTO(BaseModel):
    planet: str
    section: str = ""
    content_topic: str = ""
    difficulty_level: str = ""
    help_type: str = ""
    title: str = ""
    body_text: str = ""
    media_url: str | None = None
    display_order: int = 0
    tags: list[str] = []
    is_active: bool = True


class UpdateHelpContentDTO(BaseModel):
    section: str | None = None
    content_topic: str | None = None
    difficulty_level: str | None = None
    help_type: str | None = None
    title: str | None = None
    body_text: str | None = None
    media_url: str | None = None
    display_order: int | None = None
    tags: list[str] | None = None
    is_active: bool | None = None


class HelpContentResponseDTO(BaseModel):
    id: str
    planet: str
    section: str
    content_topic: str
    difficulty_level: str
    help_type: str
    title: str
    body_text: str
    media_url: str | None
    display_order: int
    tags: list[str]
    is_active: bool


class HelpQueryDTO(BaseModel):
    planet: str
    section: str | None = None
    content_topic: str | None = None
    difficulty_level: str | None = None
    help_type: str | None = None
    limit: int = 50
