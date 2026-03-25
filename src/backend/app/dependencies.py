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
