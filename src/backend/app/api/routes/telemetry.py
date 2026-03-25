from fastapi import APIRouter, HTTPException

from app.application.dtos.telemetry_dtos import (
    CreateTelemetryDTO,
    TelemetryResponseDTO,
)
from app.application.use_cases.telemetry_use_cases import (
    IngestTelemetryUseCase,
    ListSessionTelemetryUseCase,
)
from app.dependencies import get_telemetry_repository

router = APIRouter()


@router.post("", response_model=TelemetryResponseDTO, status_code=201)
async def ingest_telemetry(dto: CreateTelemetryDTO):
    repo = get_telemetry_repository()
    use_case = IngestTelemetryUseCase(repo)
    return await use_case.execute(dto)


@router.get("/{session_id}", response_model=list[TelemetryResponseDTO])
async def get_session_telemetry(session_id: str, limit: int = 500):
    repo = get_telemetry_repository()
    use_case = ListSessionTelemetryUseCase(repo)
    return await use_case.execute(session_id, limit=limit)
