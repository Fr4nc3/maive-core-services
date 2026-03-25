from fastapi import APIRouter

from app.api.v1.routes.students import router as students_router
from app.api.v1.routes.sessions import router as sessions_router
from app.api.v1.routes.assessments import router as assessments_router
from app.api.v1.routes.telemetry import router as telemetry_router
from app.api.v1.routes.agents import router as agents_router

router = APIRouter()
router.include_router(students_router, prefix="/students", tags=["Students"])
router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
router.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
router.include_router(agents_router, prefix="/agents", tags=["Agents"])
