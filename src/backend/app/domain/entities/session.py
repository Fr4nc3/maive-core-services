from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Session(BaseModel):
    """Domain entity representing a VR learning session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    condition: str = ""  # "maive" | "non-adaptive-vr"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    status: str = "active"  # "active" | "completed" | "abandoned"
    metadata: dict = Field(default_factory=dict)
