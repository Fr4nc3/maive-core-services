from app.application.dtos.agent_action_dtos import (
    AgentActionResponseDTO,
    CreateAgentActionDTO,
)
from app.domain.entities.agent_action import AgentAction
from app.domain.interfaces.agent_action_repository import AgentActionRepository


class CreateAgentActionUseCase:
    def __init__(self, repository: AgentActionRepository) -> None:
        self._repo = repository

    async def execute(self, dto: CreateAgentActionDTO) -> AgentActionResponseDTO:
        action = AgentAction(
            session_id=dto.session_id,
            student_id=dto.student_id,
            action_type=dto.action_type,
            agent_role=dto.agent_role,
            bot_type=dto.bot_type,
            task_id=dto.task_id,
            planet=dto.planet,
            section=dto.section,
            content=dto.content,
            trigger_reason=dto.trigger_reason,
            difficulty_from=dto.difficulty_from,
            difficulty_to=dto.difficulty_to,
            confidence=dto.confidence,
            description=dto.description,
            parameters=dto.parameters,
            student_response=dto.student_response,
        )
        created = await self._repo.create(action)
        return _to_response(created)


class ListSessionAgentActionsUseCase:
    def __init__(self, repository: AgentActionRepository) -> None:
        self._repo = repository

    async def execute(
        self, session_id: str, limit: int = 100
    ) -> list[AgentActionResponseDTO]:
        actions = await self._repo.list_by_session(session_id, limit=limit)
        return [_to_response(a) for a in actions]


def _to_response(a: AgentAction) -> AgentActionResponseDTO:
    return AgentActionResponseDTO(
        id=a.id,
        session_id=a.session_id,
        student_id=a.student_id,
        action_type=a.action_type,
        agent_role=a.agent_role,
        bot_type=a.bot_type,
        task_id=a.task_id,
        planet=a.planet,
        section=a.section,
        content=a.content,
        trigger_reason=a.trigger_reason,
        difficulty_from=a.difficulty_from,
        difficulty_to=a.difficulty_to,
        confidence=a.confidence,
        description=a.description,
        parameters=a.parameters,
        student_response=a.student_response,
        triggered_at=a.triggered_at.isoformat(),
    )
