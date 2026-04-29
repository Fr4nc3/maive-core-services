"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: Repository port (Clean Architecture).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.arcs_survey import ARCSSurveyResponse


class ARCSSurveyRepository(ABC):
    """Port for ARCS survey response persistence."""

    @abstractmethod
    async def create(self, response: ARCSSurveyResponse) -> ARCSSurveyResponse: ...

    @abstractmethod
    async def list_by_session(self, session_id: str) -> list[ARCSSurveyResponse]: ...

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[ARCSSurveyResponse]: ...
