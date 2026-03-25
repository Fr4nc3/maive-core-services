from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class AgentAction(BaseModel):
    """Domain entity for AI agent adaptation actions."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    action_type: str = ""  # "scaffold" | "hint" | "difficulty_adjust" | "feedback"
    description: str = ""
    parameters: dict = Field(default_factory=dict)
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
