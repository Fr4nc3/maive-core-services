from abc import ABC, abstractmethod

from app.domain.entities.qualitative_feedback import QualitativeFeedback


class QualitativeFeedbackRepository(ABC):
    """Port for qualitative feedback persistence."""

    @abstractmethod
    async def create(self, feedback: QualitativeFeedback) -> QualitativeFeedback: ...

    @abstractmethod
    async def list_by_session(self, session_id: str) -> list[QualitativeFeedback]: ...
