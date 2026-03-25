from pydantic import BaseModel


class CreateStudentDTO(BaseModel):
    spatial_id: str
    group: str = ""
    metadata: dict = {}


class UpdateStudentDTO(BaseModel):
    group: str | None = None
    metadata: dict | None = None


class StudentResponseDTO(BaseModel):
    id: str
    spatial_id: str
    group: str
    created_at: str
    metadata: dict
