"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateAssessmentDTO(BaseModel):
    user_id: str
    session_id: str | None = None
    assessment_type: str = ""
    score: float = 0.0
    max_score: float = 100.0
    responses: list[dict] = []
    metadata: dict = {}


class AssessmentResponseDTO(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    assessment_type: str
    score: float
    max_score: float
    normalized_gain: float | None
    submitted_at: str
    metadata: dict
