"""Domain entity for the 5-platform research data model.

Pillar: Stable Core
Phase: B
Purpose: Domain entity for the 5-platform research data model.
Documented in: plan/architecture.md
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ARCSSurveyResponse(BaseModel):
    """Domain entity for ARCS engagement survey responses (RQ2)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    module_id: str = ""
    attention_score: float = 0.0
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    satisfaction_score: float = 0.0
    composite_score: float = 0.0
    item_responses: list[dict] = Field(
        default_factory=list,
    )  # [{item_id, dimension, value, response_time_ms}]
    completion_time_ms: int = 0
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
