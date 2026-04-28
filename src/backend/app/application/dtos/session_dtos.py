from pydantic import BaseModel


class CreateSessionDTO(BaseModel):
    student_id: str
    platform: str = ""
    condition: str = ""
    difficulty_level: str = ""
    # "en" | "es" — if None, falls back to student.preferred_language (DEC-014)
    language: str | None = None
    metadata: dict = {}


class UpdateSessionDTO(BaseModel):
    status: str | None = None
    difficulty_level: str | None = None
    language: str | None = None
    metadata: dict | None = None


class SessionResponseDTO(BaseModel):
    id: str
    student_id: str
    platform: str
    condition: str
    difficulty_level: str
    language: str
    started_at: str
    ended_at: str | None
    status: str
    metadata: dict
