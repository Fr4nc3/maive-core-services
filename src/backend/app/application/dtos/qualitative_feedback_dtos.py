"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateQualitativeFeedbackDTO(BaseModel):
    session_id: str
    user_id: str
    prompt: str = ""
    arcs_dimension: str | None = None
    response_text: str = ""


class QualitativeFeedbackResponseDTO(BaseModel):
    id: str
    session_id: str
    user_id: str
    prompt: str
    arcs_dimension: str | None
    response_text: str
    submitted_at: str
    theme_codes: list[str]
