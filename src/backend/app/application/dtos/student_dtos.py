from pydantic import BaseModel


class IdentifyStudentDTO(BaseModel):
    """Idempotent identity payload sent by every client on first interaction."""

    platform: str  # "spatial.io" | "vrchat" | "sinespace" | "unity" | "web"
    platform_user_id: str
    display_name: str = ""
    metadata: dict = {}


class CreateStudentDTO(BaseModel):
    platform: str
    platform_user_id: str
    display_name: str = ""
    metadata: dict = {}


class UpdateStudentDTO(BaseModel):
    display_name: str | None = None
    metadata: dict | None = None


class StudentResponseDTO(BaseModel):
    id: str
    platform: str
    platform_user_id: str
    display_name: str
    created_at: str
    metadata: dict
