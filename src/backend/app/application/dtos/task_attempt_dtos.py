"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateTaskAttemptDTO(BaseModel):
    session_id: str
    student_id: str
    task_id: str
    task_name: str = ""
    task_type: str = ""
    planet: str = ""
    section: str = ""
    difficulty_level: str = ""
    total_steps: int = 0


class UpdateTaskAttemptDTO(BaseModel):
    steps_completed: int | None = None
    total_time_ms: int | None = None
    total_errors: int | None = None
    total_retries: int | None = None
    total_hints_requested: int | None = None
    total_hints_delivered: int | None = None
    trajectory_revisions: int | None = None
    score: float | None = None
    success: bool | None = None
    status: str | None = None
    step_details: list[dict] | None = None
    rater_scores: list[dict] | None = None


class TaskAttemptResponseDTO(BaseModel):
    id: str
    session_id: str
    student_id: str
    task_id: str
    task_name: str
    task_type: str
    planet: str
    section: str
    difficulty_level: str
    started_at: str
    completed_at: str | None
    status: str
    total_steps: int
    steps_completed: int
    total_time_ms: int
    total_errors: int
    total_retries: int
    total_hints_requested: int
    total_hints_delivered: int
    trajectory_revisions: int
    score: float | None
    success: bool | None
    rater_scores: list[dict]
    step_details: list[dict]
