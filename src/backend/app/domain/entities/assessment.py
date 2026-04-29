"""Domain entity for the 5-platform research data model.

Pillar: Stable Core
Phase: B
Purpose: Domain entity for the 5-platform research data model.
Documented in: plan/architecture.md
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


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
    rater_scores: list[dict] = Field(default_factory=list)  # [{rater_id, score, notes}]
    rubric_threshold: float | None = None  # success threshold for classifier label
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
