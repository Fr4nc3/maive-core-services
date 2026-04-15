import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HelpContent(BaseModel):
    """Domain entity for static (hardcoded) bot help content."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    planet: str  # partition key, e.g. "mars", "jupiter"
    section: str = ""  # area within planet, e.g. "crater_lab"
    content_topic: str = ""  # e.g. "orbital-mechanics", "atmosphere"
    difficulty_level: str = ""  # "easy" | "medium" | "hard"
    help_type: str = ""  # "hint" | "explanation" | "fact" | "quiz_feedback"
    title: str = ""
    body_text: str = ""
    media_url: str | None = None
    display_order: int = 0
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
