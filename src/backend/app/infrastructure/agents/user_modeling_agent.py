"""
User Modeling Agent.

Analyzes session telemetry to produce a learner profile with engagement metrics,
knowledge gaps, and an initial action recommendation.

Pillar: Configuration Layer
Phase: R
Purpose: Multi-agent layer; system prompts and decision logic.
Documented in: docs/paper/maive-systems-engineering-extended.md
"""

import json
import logging
from pathlib import Path

from app.domain.entities.telemetry import TelemetryEvent
from app.domain.interfaces.telemetry_repository import TelemetryRepository
from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "user_modeling.txt"


class UserModelingAgent:
    def __init__(
        self,
        llm: LLMProvider,
        telemetry_repo: TelemetryRepository,
    ) -> None:
        self._llm = llm
        self._telemetry_repo = telemetry_repo
        self._system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    async def build_profile(
        self,
        session_id: str,
        session_data: dict,
    ) -> dict:
        events = await self._telemetry_repo.list_by_session(session_id)
        summary = self._summarize_events(events)
        recent = self._recent_events(events, n=20)

        user_msg = json.dumps(
            {
                "session": session_data,
                "telemetry_summary": summary,
                "recent_events": recent,
            },
            default=str,
        )

        response = await self._llm.chat(
            messages=[
                ChatMessage(role="system", content=self._system_prompt),
                ChatMessage(role="user", content=user_msg),
            ],
            temperature=0.2,
            max_tokens=512,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("User Modeling Agent returned non-JSON: %s", response.content)
            return self._fallback_profile(summary)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _summarize_events(events: list[TelemetryEvent]) -> dict:
        total = len(events)
        idle = sum(1 for e in events if e.event_type == "IDLE_DETECTED")
        help_req = sum(1 for e in events if e.event_type == "HELP_REQUESTED")
        errors = sum(1 for e in events if e.event_type == "ERROR_COMMITTED")
        tasks_started = sum(1 for e in events if e.event_type == "TASK_STARTED")
        tasks_completed = sum(1 for e in events if e.event_type == "TASK_COMPLETED")
        retries = sum(1 for e in events if e.event_type == "RETRY_ATTEMPTED")
        sections = {e.section for e in events if e.section}

        return {
            "total_events": total,
            "idle_count": idle,
            "help_requested_count": help_req,
            "errors_count": errors,
            "tasks_started": tasks_started,
            "tasks_completed": tasks_completed,
            "retries": retries,
            "sections_visited": list(sections),
        }

    @staticmethod
    def _recent_events(events: list[TelemetryEvent], n: int = 20) -> list[dict]:
        sorted_events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:n]
        return [
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "planet": e.planet,
                "section": e.section,
                "duration_ms": e.duration_ms,
            }
            for e in sorted_events
        ]

    @staticmethod
    def _fallback_profile(summary: dict) -> dict:
        total = max(summary["total_events"], 1)
        tasks = max(summary["tasks_started"], 1)
        errors = summary["errors_count"]
        return {
            "engagement_level": "medium",
            "idle_rate": summary["idle_count"] / total,
            "hint_rate": summary["help_requested_count"] / tasks,
            "error_rate": errors / tasks,
            "persistence_score": summary["retries"] / max(errors, 1),
            "completion_rate": summary["tasks_completed"] / tasks,
            "current_planet": "",
            "current_section": "",
            "difficulty_fit": "appropriate",
            "knowledge_gaps": [],
            "recommended_action": "none",
            "reasoning": "Fallback profile — LLM response could not be parsed.",
        }
