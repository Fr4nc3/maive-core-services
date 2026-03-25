from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class TelemetryEventType(str, Enum):
    """All VR behavioral event types tracked by MAIVE."""

    # Help Interactions (primary telemetry)
    HELP_REQUESTED = "HELP_REQUESTED"  # User clicked for help
    HELP_DELIVERED = "HELP_DELIVERED"  # Bot delivered help response
    HELP_DISMISSED = "HELP_DISMISSED"  # User dismissed the help
    HELP_FOLLOWED = "HELP_FOLLOWED"  # User acted on help suggestion

    # Section Navigation
    SECTION_ENTERED = "SECTION_ENTERED"  # User entered a planet/section
    SECTION_EXITED = "SECTION_EXITED"  # User left a planet/section

    # Task Interaction
    TASK_STARTED = "TASK_STARTED"
    TASK_STEP_COMPLETED = "TASK_STEP_COMPLETED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_ABANDONED = "TASK_ABANDONED"

    # Errors & Retries
    ERROR_COMMITTED = "ERROR_COMMITTED"
    RETRY_ATTEMPTED = "RETRY_ATTEMPTED"

    # Assessment
    QUIZ_ANSWER_SUBMITTED = "QUIZ_ANSWER_SUBMITTED"
    SURVEY_COMPLETED = "SURVEY_COMPLETED"

    # Agent Interaction
    AGENT_PROMPT_DISPLAYED = "AGENT_PROMPT_DISPLAYED"
    AGENT_PROMPT_DISMISSED = "AGENT_PROMPT_DISMISSED"
    AGENT_PROMPT_FOLLOWED = "AGENT_PROMPT_FOLLOWED"

    # Session Lifecycle
    SESSION_PAUSED = "SESSION_PAUSED"
    SESSION_RESUMED = "SESSION_RESUMED"
    MODULE_ENTERED = "MODULE_ENTERED"
    MODULE_EXITED = "MODULE_EXITED"


class TelemetryEvent(BaseModel):
    """Domain entity for VR behavioral telemetry data."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    event_type: str = ""  # value from TelemetryEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int | None = None
    section: str = ""  # planet or area, e.g. "mars", "jupiter", "solar-system"
    content: str = ""  # content topic, e.g. "orbital-mechanics", "atmosphere"
    help_text: str = ""  # the help content shown to the user
    bot_type: str = ""  # "hardcoded" | "ai" — which bot provided the help
    payload: dict = Field(default_factory=dict)
