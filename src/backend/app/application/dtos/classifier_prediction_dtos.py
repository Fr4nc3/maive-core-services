from pydantic import BaseModel


class CreateClassifierPredictionDTO(BaseModel):
    session_id: str
    student_id: str
    model_version: str = ""
    features_used: dict = {}
    predicted_probability: float = 0.0
    predicted_label: int = 0
    actual_label: int | None = None
    actual_score: float | None = None
    confidence_interval: dict | None = None


class ClassifierPredictionResponseDTO(BaseModel):
    id: str
    session_id: str
    student_id: str
    model_version: str
    features_used: dict
    predicted_probability: float
    predicted_label: int
    actual_label: int | None
    actual_score: float | None
    confidence_interval: dict | None
    created_at: str
