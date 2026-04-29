"""
Coordination Agent.

Orchestrates User Modeling, Content Curation, and Assessment agents to produce
a single cohesive action for the user's current VR session.
Records the decision as an AgentAction entity in the database.

Pillar: Configuration Layer
Phase: R
Purpose: Multi-agent layer; system prompts and decision logic.
Documented in: docs/paper/maive-systems-engineering-extended.md
"""

import json
import logging
from pathlib import Path

from app.domain.entities.agent_action import AgentAction
from app.domain.interfaces.agent_action_repository import AgentActionRepository
from app.domain.interfaces.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.domain.interfaces.session_repository import SessionRepository
from app.domain.interfaces.task_attempt_repository import TaskAttemptRepository
from app.domain.interfaces.telemetry_repository import TelemetryRepository
from app.infrastructure.agents.assessment_agent import AssessmentAgent
from app.infrastructure.agents.content_curation_agent import ContentCurationAgent
from app.infrastructure.agents.user_modeling_agent import UserModelingAgent
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "coordination.txt"


class CoordinationAgent:
    """Top-level orchestrator: runs the full adaptive pipeline for a session."""

    def __init__(
        self,
        llm: LLMProvider,
        telemetry_repo: TelemetryRepository,
        session_repo: SessionRepository,
        task_attempt_repo: TaskAttemptRepository,
        agent_action_repo: AgentActionRepository,
        knowledge_repo: KnowledgeDocumentRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self._llm = llm
        self._session_repo = session_repo
        self._task_attempt_repo = task_attempt_repo
        self._agent_action_repo = agent_action_repo
        self._system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

        # Sub-agents
        self._user_modeling = UserModelingAgent(llm, telemetry_repo)
        self._content_curation = ContentCurationAgent(llm, knowledge_repo, embedding_service)
        self._assessment = AssessmentAgent(llm)

    async def evaluate_session(self, session_id: str, help_query: str | None = None) -> dict:
        """Run the full multi-agent pipeline and return the coordinated action."""

        # 1. Fetch session
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            return {"action_type": "no_action", "reasoning": "Session not found."}

        # Control group: never adapt
        if session.condition == "non-adaptive-vr":
            return {
                "action_type": "no_action",
                "content": "",
                "confidence": 1.0,
                "trigger_reason": "control_group",
                "reasoning": "Session is in the non-adaptive (control) condition.",
            }

        session_data = {
            "user_id": session.user_id,
            "platform": session.platform,
            "difficulty_level": session.difficulty_level,
            "total_duration_ms": session.total_duration_ms,
            "total_hints_requested": session.total_hints_requested,
            "total_errors": session.total_errors,
            "total_tasks_completed": session.total_tasks_completed,
        }

        # 2. User Modeling
        profile = await self._user_modeling.build_profile(session_id, session_data)

        # 3. Assessment
        task_attempts = await self._task_attempt_repo.list_by_session(session_id)
        recent_attempts = [
            {
                "task_name": t.task_name,
                "status": t.status,
                "score": t.score,
                "total_errors": t.total_errors,
                "total_retries": t.total_retries,
            }
            for t in task_attempts[-10:]
        ]

        assessment = await self._assessment.assess(
            learner_profile=profile,
            current_difficulty=session.difficulty_level or "medium",
            session_context={
                "planet": profile.get("current_planet", ""),
                "section": profile.get("current_section", ""),
                "tasks_completed": session.total_tasks_completed,
                "total_tasks": len(task_attempts),
                "total_duration_ms": session.total_duration_ms,
            },
            recent_task_attempts=recent_attempts,
        )

        # 4. Content Curation (only if a help query or action recommended)
        content_result = None
        if help_query:
            content_result = await self._content_curation.curate(
                learner_profile=profile,
                query=help_query,
                help_type="explanation",
            )
        elif profile.get("recommended_action") in ("hint", "scaffold"):
            gaps = profile.get("knowledge_gaps", [])
            query = gaps[0] if gaps else profile.get("current_section", "general help")
            content_result = await self._content_curation.curate(
                learner_profile=profile,
                query=query,
                help_type=profile["recommended_action"],
            )

        # 5. Coordination LLM call
        coord_input = json.dumps(
            {
                "user_model": profile,
                "assessment": assessment,
                "content": content_result,
                "session": {
                    "session_id": session_id,
                    "user_id": session.user_id,
                    "platform": session.platform,
                    "planet": profile.get("current_planet", ""),
                    "section": profile.get("current_section", ""),
                    "condition": session.condition,
                },
            },
            default=str,
        )

        response = await self._llm.chat(
            messages=[
                ChatMessage(role="system", content=self._system_prompt),
                ChatMessage(role="user", content=coord_input),
            ],
            temperature=0.2,
            max_tokens=512,
        )

        try:
            action = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Coordination Agent returned non-JSON: %s", response.content)
            action = {
                "action_type": "no_action",
                "content": "",
                "difficulty_from": "",
                "difficulty_to": "",
                "confidence": 0.0,
                "trigger_reason": "parse_error",
                "agent_role": "",
                "reasoning": "Fallback — LLM response could not be parsed.",
            }

        # 6. Persist the agent action
        if action.get("action_type") != "no_action":
            record = AgentAction(
                session_id=session_id,
                user_id=session.user_id,
                action_type=action.get("action_type", ""),
                agent_role=action.get("agent_role", ""),
                bot_type="ai",
                planet=profile.get("current_planet", ""),
                section=profile.get("current_section", ""),
                content=action.get("content", ""),
                trigger_reason=action.get("trigger_reason", ""),
                difficulty_from=action.get("difficulty_from", ""),
                difficulty_to=action.get("difficulty_to", ""),
                confidence=action.get("confidence", 0.0),
                description=action.get("reasoning", ""),
                parameters={
                    "user_model": profile,
                    "assessment": assessment,
                },
            )
            await self._agent_action_repo.create(record)

        return action
