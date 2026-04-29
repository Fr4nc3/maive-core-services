"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateARCSSurveyDTO(BaseModel):
    session_id: str
    user_id: str
    module_id: str = ""
    attention_score: float = 0.0
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    satisfaction_score: float = 0.0
    item_responses: list[dict] = []
    completion_time_ms: int = 0


class ARCSSurveyResponseDTO(BaseModel):
    id: str
    session_id: str
    user_id: str
    module_id: str
    attention_score: float
    relevance_score: float
    confidence_score: float
    satisfaction_score: float
    composite_score: float
    item_responses: list[dict]
    completion_time_ms: int
    submitted_at: str
