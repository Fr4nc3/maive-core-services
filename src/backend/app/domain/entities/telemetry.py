from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class TelemetryEvent(BaseModel):
    """Domain entity for VR behavioral telemetry data."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    event_type: str = ""  # "hint_request" | "error" | "task_complete" | "idle" | ...
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int | None = None
    position: dict = Field(default_factory=dict)  # x, y, z in VR space
    payload: dict = Field(default_factory=dict)
