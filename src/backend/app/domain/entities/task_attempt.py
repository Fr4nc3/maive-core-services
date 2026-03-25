from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class TaskAttempt(BaseModel):
    """Domain entity tracking a student's attempt at an open-ended VR challenge (RQ3)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    task_id: str
    task_name: str = ""
    task_type: str = ""  # "orbital_trajectory" | "stellar_classification" | "gravitational_sim"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    status: str = "in_progress"  # "in_progress" | "completed" | "abandoned"
    total_steps: int = 0
    steps_completed: int = 0
    total_time_ms: int = 0
    total_errors: int = 0
    total_retries: int = 0
    total_hints_requested: int = 0
    total_hints_delivered: int = 0
    trajectory_revisions: int = 0
    score: float | None = None
    success: bool | None = None
    rater_scores: list[dict] = Field(default_factory=list)  # [{rater_id, score}]
    step_details: list[dict] = Field(default_factory=list)  # [{step_index, time_ms, errors, hints, result}]
    metadata: dict = Field(default_factory=dict)
