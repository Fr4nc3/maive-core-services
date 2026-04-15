from pydantic import BaseModel


class CreateSessionDTO(BaseModel):
    student_id: str
    platform: str = ""
    condition: str = ""
    difficulty_level: str = ""
    metadata: dict = {}


class UpdateSessionDTO(BaseModel):
    status: str | None = None
    difficulty_level: str | None = None
    metadata: dict | None = None


class SessionResponseDTO(BaseModel):
    id: str
    student_id: str
    platform: str
    condition: str
    difficulty_level: str
    started_at: str
    ended_at: str | None
    status: str
    metadata: dict
