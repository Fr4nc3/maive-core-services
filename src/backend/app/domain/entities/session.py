import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Session(BaseModel):
    """Domain entity representing a VR learning session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    platform: str = ""  # "spatial.io" | "vrchat" | "sinespace" | "web"
    condition: str = ""  # "maive" | "non-adaptive-vr"
    module_id: str = ""
    vr_device: str = ""  # "quest" | "pcvr" | "desktop"
    difficulty_level: str = ""  # current adaptive difficulty, e.g. "easy" | "medium" | "hard"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    status: str = "active"  # "active" | "completed" | "abandoned"
    total_duration_ms: int | None = None
    total_hints_requested: int = 0
    total_errors: int = 0
    total_tasks_completed: int = 0
    metadata: dict = Field(default_factory=dict)
