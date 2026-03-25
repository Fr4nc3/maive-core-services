from app.infrastructure.persistence.cosmos_db.client import get_cosmos_client
from app.infrastructure.persistence.cosmos_db.student_repository import (
    CosmosStudentRepository,
)
from app.infrastructure.persistence.cosmos_db.session_repository import (
    CosmosSessionRepository,
)
from app.infrastructure.persistence.cosmos_db.assessment_repository import (
    CosmosAssessmentRepository,
)
from app.infrastructure.persistence.cosmos_db.telemetry_repository import (
    CosmosTelemetryRepository,
)
from app.infrastructure.persistence.cosmos_db.task_attempt_repository import (
    CosmosTaskAttemptRepository,
)
from app.infrastructure.persistence.cosmos_db.arcs_survey_repository import (
    CosmosARCSSurveyRepository,
)
from app.infrastructure.persistence.cosmos_db.qualitative_feedback_repository import (
    CosmosQualitativeFeedbackRepository,
)
from app.infrastructure.persistence.cosmos_db.classifier_prediction_repository import (
    CosmosClassifierPredictionRepository,
)
from app.config import settings


def get_student_repository() -> CosmosStudentRepository:
    client = get_cosmos_client()
    return CosmosStudentRepository(client, settings.cosmos_database)


def get_session_repository() -> CosmosSessionRepository:
    client = get_cosmos_client()
    return CosmosSessionRepository(client, settings.cosmos_database)


def get_assessment_repository() -> CosmosAssessmentRepository:
    client = get_cosmos_client()
    return CosmosAssessmentRepository(client, settings.cosmos_database)


def get_telemetry_repository() -> CosmosTelemetryRepository:
    client = get_cosmos_client()
    return CosmosTelemetryRepository(client, settings.cosmos_database)


def get_task_attempt_repository() -> CosmosTaskAttemptRepository:
    client = get_cosmos_client()
    return CosmosTaskAttemptRepository(client, settings.cosmos_database)


def get_arcs_survey_repository() -> CosmosARCSSurveyRepository:
    client = get_cosmos_client()
    return CosmosARCSSurveyRepository(client, settings.cosmos_database)


def get_qualitative_feedback_repository() -> CosmosQualitativeFeedbackRepository:
    client = get_cosmos_client()
    return CosmosQualitativeFeedbackRepository(client, settings.cosmos_database)


def get_classifier_prediction_repository() -> CosmosClassifierPredictionRepository:
    client = get_cosmos_client()
    return CosmosClassifierPredictionRepository(client, settings.cosmos_database)
