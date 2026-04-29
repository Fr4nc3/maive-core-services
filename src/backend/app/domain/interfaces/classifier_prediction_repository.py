"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: Repository port (Clean Architecture).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.classifier_prediction import ClassifierPrediction


class ClassifierPredictionRepository(ABC):
    """Port for classifier prediction persistence."""

    @abstractmethod
    async def create(self, prediction: ClassifierPrediction) -> ClassifierPrediction: ...

    @abstractmethod
    async def get_by_session(self, session_id: str) -> ClassifierPrediction | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[ClassifierPrediction]: ...
