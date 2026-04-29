"""Use case orchestrating domain + repository ports.

Pillar: Stable Core
Phase: B
Purpose: Use case orchestrating domain + repository ports.
Documented in: plan/architecture.md
"""

from app.application.dtos.task_attempt_dtos import (
    CreateTaskAttemptDTO,
    TaskAttemptResponseDTO,
    UpdateTaskAttemptDTO,
)
from app.domain.entities.task_attempt import TaskAttempt
from app.domain.interfaces.task_attempt_repository import TaskAttemptRepository


class CreateTaskAttemptUseCase:
    def __init__(self, repository: TaskAttemptRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateTaskAttemptDTO) -> TaskAttemptResponseDTO:
        attempt = TaskAttempt(
            session_id=dto.session_id,
            student_id=dto.student_id,
            task_id=dto.task_id,
            task_name=dto.task_name,
            task_type=dto.task_type,
            planet=dto.planet,
            section=dto.section,
            difficulty_level=dto.difficulty_level,
            total_steps=dto.total_steps,
        )
        created = await self._repo.create(attempt)
        return _to_response(created)


class UpdateTaskAttemptUseCase:
    def __init__(self, repository: TaskAttemptRepository) -> None:
        self._repo = repository

    async def execute(
        self, attempt_id: str, session_id: str, dto: UpdateTaskAttemptDTO
    ) -> TaskAttemptResponseDTO:
        attempt = await self._repo.get_by_id(attempt_id, session_id)
        if not attempt:
            raise ValueError(f"TaskAttempt {attempt_id} not found")
        update_data = dto.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(attempt, key, value)
        updated = await self._repo.update(attempt)
        return _to_response(updated)


class ListSessionTaskAttemptsUseCase:
    def __init__(self, repository: TaskAttemptRepository) -> None:
        self._repo = repository

    async def execute(self, session_id: str) -> list[TaskAttemptResponseDTO]:
        attempts = await self._repo.list_by_session(session_id)
        return [_to_response(a) for a in attempts]


def _to_response(a: TaskAttempt) -> TaskAttemptResponseDTO:
    return TaskAttemptResponseDTO(
        id=a.id,
        session_id=a.session_id,
        student_id=a.student_id,
        task_id=a.task_id,
        task_name=a.task_name,
        task_type=a.task_type,
        planet=a.planet,
        section=a.section,
        difficulty_level=a.difficulty_level,
        started_at=a.started_at.isoformat(),
        completed_at=a.completed_at.isoformat() if a.completed_at else None,
        status=a.status,
        total_steps=a.total_steps,
        steps_completed=a.steps_completed,
        total_time_ms=a.total_time_ms,
        total_errors=a.total_errors,
        total_retries=a.total_retries,
        total_hints_requested=a.total_hints_requested,
        total_hints_delivered=a.total_hints_delivered,
        trajectory_revisions=a.trajectory_revisions,
        score=a.score,
        success=a.success,
        rater_scores=a.rater_scores,
        step_details=a.step_details,
    )
