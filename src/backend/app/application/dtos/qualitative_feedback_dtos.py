from pydantic import BaseModel


class CreateQualitativeFeedbackDTO(BaseModel):
    session_id: str
    student_id: str
    prompt: str = ""
    arcs_dimension: str | None = None
    response_text: str = ""


class QualitativeFeedbackResponseDTO(BaseModel):
    id: str
    session_id: str
    student_id: str
    prompt: str
    arcs_dimension: str | None
    response_text: str
    submitted_at: str
    theme_codes: list[str]
