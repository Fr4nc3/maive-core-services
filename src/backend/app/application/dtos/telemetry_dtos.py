"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateTelemetryDTO(BaseModel):
    session_id: str
    student_id: str
    event_type: str = ""
    duration_ms: int | None = None
    planet: str = ""
    section: str = ""
    content: str = ""
    help_text: str = ""  # help content shown
    bot_type: str = ""  # "hardcoded" | "ai"
    payload: dict = {}


class TelemetryResponseDTO(BaseModel):
    id: str
    session_id: str
    student_id: str
    event_type: str
    timestamp: str
    duration_ms: int | None
    planet: str
    section: str
    content: str
    help_text: str
    bot_type: str
    payload: dict
