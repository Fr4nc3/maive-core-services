from abc import ABC, abstractmethod

from app.domain.entities.task_attempt import TaskAttempt


class TaskAttemptRepository(ABC):
    """Port for task attempt persistence."""

    @abstractmethod
    async def create(self, attempt: TaskAttempt) -> TaskAttempt: ...

    @abstractmethod
    async def update(self, attempt: TaskAttempt) -> TaskAttempt: ...

    @abstractmethod
    async def get_by_id(self, attempt_id: str, session_id: str) -> TaskAttempt | None: ...

    @abstractmethod
    async def list_by_session(self, session_id: str) -> list[TaskAttempt]: ...
