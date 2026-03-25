from pydantic import BaseModel


class CreateSessionDTO(BaseModel):
    student_id: str
    condition: str = ""
    metadata: dict = {}


class UpdateSessionDTO(BaseModel):
    status: str | None = None
    metadata: dict | None = None


class SessionResponseDTO(BaseModel):
    id: str
    student_id: str
    condition: str
    started_at: str
    ended_at: str | None
    status: str
    metadata: dict
