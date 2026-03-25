from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Student(BaseModel):
    """Domain entity representing a learner in the MAIVE platform."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    spatial_id: str  # Spatial.io user identifier
    group: str = ""  # e.g. "maive" or "non-adaptive-vr"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
