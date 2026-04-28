# Documented in: docs/paper/maive-systems-engineering-extended.md#81-identity-model
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Student(BaseModel):
    """Domain entity representing a learner in the MAIVE platform.

    Identity natural key: ``(platform, platform_user_id)``.
    Internal stable id: ``id`` (UUID), issued by the backend on first contact.
    No PII collected. ``display_name`` is optional and free-form.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str  # "spatial.io" | "vrchat" | "sinespace" | "unity" | "web"
    platform_user_id: str  # provider-issued user identifier on that platform
    display_name: str = ""
    preferred_language: str = "en"  # "en" | "es" — see DEC-014
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
