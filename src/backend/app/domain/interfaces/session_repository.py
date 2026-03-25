from abc import ABC, abstractmethod

from app.domain.entities.session import Session


class SessionRepository(ABC):
    """Port for session persistence."""

    @abstractmethod
    async def create(self, session: Session) -> Session: ...

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Session | None: ...

    @abstractmethod
    async def list_by_student(
        self, student_id: str, limit: int = 50
    ) -> list[Session]: ...

    @abstractmethod
    async def update(self, session: Session) -> Session: ...
