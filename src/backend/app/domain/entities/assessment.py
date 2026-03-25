from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Assessment(BaseModel):
    """Domain entity for pre/post test assessments."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    session_id: str | None = None
    assessment_type: str = ""  # "pre-test" | "post-test" | "transfer"
    score: float = 0.0
    max_score: float = 100.0
    normalized_gain: float | None = None
    responses: list[dict] = Field(default_factory=list)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
