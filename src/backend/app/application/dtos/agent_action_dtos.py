"""DTO for Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: DTO for Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from pydantic import BaseModel


class CreateAgentActionDTO(BaseModel):
    session_id: str
    user_id: str
    action_type: str = ""
    agent_role: str = ""
    bot_type: str = ""
    task_id: str | None = None
    planet: str = ""
    section: str = ""
    content: str = ""
    trigger_reason: str = ""
    difficulty_from: str = ""
    difficulty_to: str = ""
    confidence: float = 0.0
    description: str = ""
    parameters: dict = {}
    user_response: str | None = None


class AgentActionResponseDTO(BaseModel):
    id: str
    session_id: str
    user_id: str
    action_type: str
    agent_role: str
    bot_type: str
    task_id: str | None
    planet: str
    section: str
    content: str
    trigger_reason: str
    difficulty_from: str
    difficulty_to: str
    confidence: float
    description: str
    parameters: dict
    user_response: str | None
    triggered_at: str
