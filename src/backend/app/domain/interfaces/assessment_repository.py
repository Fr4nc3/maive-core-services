"""Repository port (Clean Architecture).

Pillar: Stable Core
Phase: B
Purpose: Repository port (Clean Architecture).
Documented in: plan/architecture.md
"""

from abc import ABC, abstractmethod

from app.domain.entities.assessment import Assessment


class AssessmentRepository(ABC):
    """Port for assessment persistence."""

    @abstractmethod
    async def create(self, assessment: Assessment) -> Assessment: ...

    @abstractmethod
    async def get_by_id(self, assessment_id: str) -> Assessment | None: ...

    @abstractmethod
    async def list_by_student(
        self, student_id: str, limit: int = 50
    ) -> list[Assessment]: ...
