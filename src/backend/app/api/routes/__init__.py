from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.arcs_surveys import router as arcs_surveys_router
from app.api.routes.assessments import router as assessments_router
from app.api.routes.bot import router as bot_router
from app.api.routes.classifier_predictions import router as classifier_predictions_router
from app.api.routes.health import router as health_router
from app.api.routes.help_content import router as help_content_router
from app.api.routes.qualitative_feedback import router as qualitative_feedback_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.students import router as students_router
from app.api.routes.task_attempts import router as task_attempts_router
from app.api.routes.telemetry import router as telemetry_router

router = APIRouter()
router.include_router(students_router, prefix="/students", tags=["Students"])
router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
router.include_router(agents_router, prefix="/agents", tags=["Agents"])
router.include_router(task_attempts_router, prefix="/task-attempts", tags=["Task Attempts"])
router.include_router(arcs_surveys_router, prefix="/arcs-surveys", tags=["ARCS Surveys"])
router.include_router(
    qualitative_feedback_router,
    prefix="/qualitative-feedback",
    tags=["Qualitative Feedback"],
)
router.include_router(
    classifier_predictions_router,
    prefix="/classifier-predictions",
    tags=["Classifier Predictions"],
)
router.include_router(help_content_router, prefix="/help", tags=["Help Content"])
router.include_router(bot_router, prefix="/bot", tags=["Bot"])
router.include_router(health_router, prefix="/health", tags=["Health"])
