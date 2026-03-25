from azure.cosmos import CosmosClient, exceptions

from app.domain.entities.student import Student
from app.domain.interfaces.student_repository import StudentRepository


class CosmosStudentRepository(StudentRepository):
    CONTAINER_NAME = "students"

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        db = client.get_database_client(database_name)
        self._container = db.get_container_client(self.CONTAINER_NAME)

    async def create(self, student: Student) -> Student:
        body = student.model_dump()
        self._container.create_item(body=body)
        return student

    async def get_by_id(self, student_id: str) -> Student | None:
        try:
            item = self._container.read_item(item=student_id, partition_key=student_id)
            return Student(**item)
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Student]:
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
        parameters = [
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ]
        items = list(
            self._container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True)
        )
        return [Student(**item) for item in items]

    async def update(self, student: Student) -> Student:
        body = student.model_dump()
        self._container.upsert_item(body=body)
        return student

    async def delete(self, student_id: str) -> bool:
        try:
            self._container.delete_item(item=student_id, partition_key=student_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
