from abc import ABC, abstractmethod

from app.domain.entities.student import Student


class StudentRepository(ABC):
    """Port for student persistence."""

    @abstractmethod
    async def create(self, student: Student) -> Student: ...

    @abstractmethod
    async def get_by_id(self, student_id: str) -> Student | None: ...

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Student]: ...

    @abstractmethod
    async def update(self, student: Student) -> Student: ...

    @abstractmethod
    async def delete(self, student_id: str) -> bool: ...
