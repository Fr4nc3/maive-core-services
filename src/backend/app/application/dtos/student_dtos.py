"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class IdentifyStudentDTO(BaseModel):
    """Idempotent identity payload sent by every client on first interaction."""

    platform: str  # "spatial.io" | "vrchat" | "sinespace" | "unity" | "web"
    platform_user_id: str
    display_name: str = ""
    preferred_language: str = "en"  # "en" | "es" — see DEC-014
    metadata: dict = {}


class CreateStudentDTO(BaseModel):
    platform: str
    platform_user_id: str
    display_name: str = ""
    preferred_language: str = "en"
    metadata: dict = {}


class UpdateStudentDTO(BaseModel):
    display_name: str | None = None
    preferred_language: str | None = None
    metadata: dict | None = None


class StudentResponseDTO(BaseModel):
    id: str
    platform: str
    platform_user_id: str
    display_name: str
    preferred_language: str
    created_at: str
    metadata: dict
