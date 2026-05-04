"""FastAPI DI container; wires registries (DEC-016) + repositories.

Pillar: Stable Core
Phase: P1
Purpose: FastAPI DI container; wires registries (DEC-016) + repositories.
Documented in: plan/architecture.md
"""

from app.config import settings
from app.infrastructure.ai.registry import LLMProviderRegistry
from app.infrastructure.persistence.cosmos_db.agent_action_repository import (
    CosmosAgentActionRepository,
)
from app.infrastructure.persistence.cosmos_db.arcs_survey_repository import (
    CosmosARCSSurveyRepository,
)
from app.infrastructure.persistence.cosmos_db.assessment_repository import (
    CosmosAssessmentRepository,
)
from app.infrastructure.persistence.cosmos_db.classifier_prediction_repository import (
    CosmosClassifierPredictionRepository,
)
from app.infrastructure.persistence.cosmos_db.client import get_cosmos_client
from app.infrastructure.persistence.cosmos_db.help_content_repository import (
    CosmosHelpContentRepository,
)
from app.infrastructure.persistence.cosmos_db.knowledge_document_repository import (
    CosmosKnowledgeDocumentRepository,
)
from app.infrastructure.persistence.cosmos_db.qualitative_feedback_repository import (
    CosmosQualitativeFeedbackRepository,
)
from app.infrastructure.persistence.cosmos_db.session_repository import (
    CosmosSessionRepository,
)
from app.infrastructure.persistence.cosmos_db.task_attempt_repository import (
    CosmosTaskAttemptRepository,
)
from app.infrastructure.persistence.cosmos_db.telemetry_repository import (
    CosmosTelemetryRepository,
)
from app.infrastructure.persistence.cosmos_db.user_repository import (
    CosmosUserRepository,
)

# ── Singletons ───────────────────────────────────────────────────────────

_llm_provider = None
_repos: dict = {}


def _get_repo(cls):
    """Return a cached repository singleton for the given class."""
    if cls not in _repos:
        client = get_cosmos_client()
        _repos[cls] = cls(client, settings.cosmos_database)
    return _repos[cls]


def build_llm_provider():
    """Build a new LLM provider from config (no caching)."""
    return LLMProviderRegistry.build(settings.llm_provider, settings)


def get_llm_provider():
    """Return a singleton LLM provider based on config."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = build_llm_provider()
    return _llm_provider


# ── Repository accessors ─────────────────────────────────────────────────

def get_user_repository():
    return _get_repo(CosmosUserRepository)


def get_session_repository():
    return _get_repo(CosmosSessionRepository)


def get_assessment_repository():
    return _get_repo(CosmosAssessmentRepository)


def get_telemetry_repository():
    return _get_repo(CosmosTelemetryRepository)


def get_task_attempt_repository():
    return _get_repo(CosmosTaskAttemptRepository)


def get_arcs_survey_repository():
    return _get_repo(CosmosARCSSurveyRepository)


def get_qualitative_feedback_repository():
    return _get_repo(CosmosQualitativeFeedbackRepository)


def get_classifier_prediction_repository():
    return _get_repo(CosmosClassifierPredictionRepository)


def get_help_content_repository():
    return _get_repo(CosmosHelpContentRepository)


def get_agent_action_repository():
    return _get_repo(CosmosAgentActionRepository)


def get_knowledge_document_repository():
    return _get_repo(CosmosKnowledgeDocumentRepository)


# ── Agent factory ─────────────────────────────────────────────────────────

def get_coordination_agent():
    """Build a CoordinationAgent wired to all dependencies."""
    from app.infrastructure.agents.coordination_agent import CoordinationAgent
    from app.infrastructure.ai.embedding_service import EmbeddingService

    llm = get_llm_provider()
    return CoordinationAgent(
        llm=llm,
        telemetry_repo=get_telemetry_repository(),
        session_repo=get_session_repository(),
        task_attempt_repo=get_task_attempt_repository(),
        agent_action_repo=get_agent_action_repository(),
        knowledge_repo=get_knowledge_document_repository(),
        embedding_service=EmbeddingService(llm),
    )
