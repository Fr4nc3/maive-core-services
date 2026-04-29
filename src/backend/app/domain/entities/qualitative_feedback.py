"""Domain entity for the 5-platform research data model.

Pillar: Stable Core
Phase: B
Purpose: Domain entity for the 5-platform research data model.
Documented in: plan/architecture.md
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QualitativeFeedback(BaseModel):
    """Domain entity for open-ended text reflections after ARCS surveys (RQ2 Task 2.3)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    prompt: str = ""
    arcs_dimension: str | None = None  # "attention" | "relevance" | "confidence" | "satisfaction"
    response_text: str = ""
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    theme_codes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
