from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class AgentAction(BaseModel):
    """Domain entity for AI agent adaptation actions."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    action_type: str = ""  # "scaffold" | "hint" | "difficulty_adjust" | "feedback"
    agent_role: str = ""  # "conceptual" | "procedural"
    bot_type: str = ""  # "hardcoded" | "ai" — hardcoded-data bot or AI-optimized bot
    task_id: str | None = None
    section: str = ""  # planet or area where action occurred
    content: str = ""  # content topic the action relates to
    trigger_reason: str = ""  # what behavioral threshold triggered this
    description: str = ""
    parameters: dict = Field(default_factory=dict)
    student_response: str | None = None  # how student reacted to the prompt
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
