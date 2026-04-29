"""
Assessment Agent.

Evaluates whether the current difficulty level is appropriate for the user
and recommends adjustments using Zone of Proximal Development principles.

Pillar: Configuration Layer
Phase: R
Purpose: Multi-agent layer; system prompts and decision logic.
Documented in: docs/paper/maive-systems-engineering-extended.md
"""

import json
import logging
from pathlib import Path

from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "assessment.txt"


class AssessmentAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm
        self._system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    async def assess(
        self,
        learner_profile: dict,
        current_difficulty: str,
        session_context: dict,
        recent_task_attempts: list[dict],
    ) -> dict:
        user_msg = json.dumps(
            {
                "learner_profile": {
                    "engagement_level": learner_profile.get("engagement_level", "medium"),
                    "idle_rate": learner_profile.get("idle_rate", 0),
                    "hint_rate": learner_profile.get("hint_rate", 0),
                    "error_rate": learner_profile.get("error_rate", 0),
                    "persistence_score": learner_profile.get("persistence_score", 0),
                    "completion_rate": learner_profile.get("completion_rate", 0),
                    "difficulty_fit": learner_profile.get("difficulty_fit", "appropriate"),
                    "knowledge_gaps": learner_profile.get("knowledge_gaps", []),
                },
                "current_difficulty": current_difficulty,
                "session_context": session_context,
                "recent_task_attempts": recent_task_attempts,
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
            logger.warning("Assessment Agent returned non-JSON: %s", response.content)
            return {
                "adjust_difficulty": False,
                "difficulty_from": current_difficulty,
                "difficulty_to": current_difficulty,
                "confidence": 0.0,
                "task_mastery_estimate": 0.5,
                "zone_of_proximal_development": "within",
                "reasoning": "Fallback — LLM response could not be parsed.",
            }
