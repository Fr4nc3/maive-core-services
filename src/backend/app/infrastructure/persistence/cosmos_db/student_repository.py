from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.domain.entities.student import Student
from app.domain.interfaces.student_repository import StudentRepository
from app.infrastructure.persistence.cosmos_db.base_repository import (
    BaseCosmosRepository,
)


class CosmosStudentRepository(BaseCosmosRepository, StudentRepository):
    CONTAINER_NAME = "students"

    async def create(self, student: Student) -> Student:
        self._container.create_item(body=student.model_dump())
        return student

    async def get_by_id(self, student_id: str) -> Student | None:
        try:
            item = self._container.read_item(item=student_id, partition_key=student_id)
            return Student(**self._strip_cosmos_meta(item))
        except CosmosResourceNotFoundError:
            return None

    async def get_by_platform_identity(
        self, platform: str, platform_user_id: str
    ) -> Student | None:
        query = (
            "SELECT TOP 1 * FROM c WHERE c.platform = @p AND c.platform_user_id = @uid"
        )
        parameters = [
            {"name": "@p", "value": platform},
            {"name": "@uid", "value": platform_user_id},
        ]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return Student(**self._strip_cosmos_meta(items[0]))

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Student]:
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
        parameters = [
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )
        return [Student(**item) for item in items]

    async def update(self, student: Student) -> Student:
        self._container.upsert_item(body=student.model_dump())
        return student

    async def delete(self, student_id: str) -> bool:
        try:
            self._container.delete_item(item=student_id, partition_key=student_id)
            return True
        except CosmosResourceNotFoundError:
            return False
