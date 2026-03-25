from pydantic import BaseModel


class CreateTelemetryDTO(BaseModel):
    session_id: str
    student_id: str
    event_type: str = ""
    duration_ms: int | None = None
    position: dict = {}
    payload: dict = {}


class TelemetryResponseDTO(BaseModel):
    id: str
    session_id: str
    student_id: str
    event_type: str
    timestamp: str
    duration_ms: int | None
    position: dict
    payload: dict
