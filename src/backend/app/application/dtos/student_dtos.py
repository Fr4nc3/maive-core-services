from pydantic import BaseModel


class CreateStudentDTO(BaseModel):
    email: str
    display_name: str
    group: str = ""
    metadata: dict = {}


class UpdateStudentDTO(BaseModel):
    display_name: str | None = None
    group: str | None = None
    metadata: dict | None = None


class StudentResponseDTO(BaseModel):
    id: str
    email: str
    display_name: str
    group: str
    created_at: str
    metadata: dict
