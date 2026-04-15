import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ClassifierPrediction(BaseModel):
    """Domain entity for Random Forest classifier outputs (RQ3 Task 3.3)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    model_version: str = ""
    features_used: dict = Field(default_factory=dict)
    predicted_probability: float = 0.0
    predicted_label: int = 0  # 0 = failure, 1 = success
    actual_label: int | None = None
    actual_score: float | None = None
    confidence_interval: dict | None = None  # {lower, upper}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
