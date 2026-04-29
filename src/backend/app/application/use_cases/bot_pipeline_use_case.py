"""Orchestrates the 6-stage RAI bot pipeline (DEC-019).

Pillar: Stable Core
Phase: R
Purpose: Orchestrates the 6-stage RAI bot pipeline (DEC-019).
Documented in: docs/rai-policy.md#pipeline
"""

from dataclasses import dataclass

from app.domain.interfaces.bot_audit_repository import BotAuditRepository
from app.infrastructure.rai import (
    input_validator,
    output_validator,
    prompt_injection,
    system_prompt,
    topic_gate,
)
from app.infrastructure.rai.audit import AuditDraft
from app.infrastructure.rai.errors import BotPipelineError


@dataclass
class BotPipelineRequest:
    session_id: str
    student_id: str
    query: str
    language: str = "en"
    bot_path: str = "ai"  # "ai" | "static"
    client_platform: str = ""
    client_version: str = ""


@dataclass
class BotPipelineResult:
    """Outcome of one pipeline run."""

    content: str
    action_type: str = "explanation"
    confidence: float = 0.0
    source: str = ""
    system_prompt_id: str = ""
    topic_gate_score: float = 0.0
    prompt_injection_score: float = 0.0


class BotPipelineUseCase:
    """Owns the 6-stage RAI pipeline for /api/bot/ask.

    Inputs an agent-callable + an audit repo so it stays decoupled
    from CoordinationAgent (testable with a fake).
    """

    def __init__(
        self,
        coordination_agent,
        audit_repo: BotAuditRepository,
        llm_provider_name: str = "",
        llm_model_name: str = "",
    ) -> None:
        self._agent = coordination_agent
        self._audit = audit_repo
        self._llm_provider_name = llm_provider_name
        self._llm_model_name = llm_model_name

    async def execute(self, req: BotPipelineRequest) -> BotPipelineResult:
        draft = AuditDraft(
            session_id=req.session_id,
            student_id=req.student_id,
            language=req.language,
            bot_path=req.bot_path,
            client_platform=req.client_platform,
            client_version=req.client_version,
            llm_provider=self._llm_provider_name,
            llm_model=self._llm_model_name,
        )
        draft.set_query(req.query)

        try:
            cleaned = input_validator.validate(req.query, req.language)
            draft.set_query(cleaned)

            draft.topic_gate_score = topic_gate.check(cleaned)

            draft.prompt_injection_score = prompt_injection.check(cleaned)

            prompt_id = system_prompt.default_id_for(req.language)
            draft.system_prompt_id = prompt_id

            agent_result: dict = await self._agent.evaluate_session(
                req.session_id, help_query=cleaned
            )
            content = str(agent_result.get("content", "") or "")

            output_validator.check(content)
            draft.output_validator_pass = True
            draft.output_validator_reasons = []

            return BotPipelineResult(
                content=content,
                action_type=str(agent_result.get("action_type", "explanation")),
                confidence=float(agent_result.get("confidence", 0.0) or 0.0),
                source=str(agent_result.get("trigger_reason", "") or ""),
                system_prompt_id=prompt_id,
                topic_gate_score=draft.topic_gate_score,
                prompt_injection_score=draft.prompt_injection_score,
            )
        except BotPipelineError as exc:
            self._record_failure(draft, exc)
            raise
        finally:
            await self._persist(draft)

    # ── helpers ─────────────────────────────────────────────────────

    def _record_failure(self, draft: AuditDraft, exc: BotPipelineError) -> None:
        draft.error_code = f"{exc.stage}:{exc.public_detail}"
        if exc.stage == "input_validator":
            draft.input_validator_pass = False
            draft.input_validator_reason = exc.reason
        elif exc.stage == "topic_gate":
            draft.topic_gate_pass = False
        elif exc.stage == "prompt_injection":
            draft.prompt_injection_blocked = True
        elif exc.stage == "output_validator":
            draft.output_validator_pass = False
            draft.output_validator_reasons = exc.reason.split(",")

    async def _persist(self, draft: AuditDraft) -> None:
        try:
            await self._audit.create(draft.to_audit())
        except Exception:  # noqa: BLE001 — audit must never break the request
            # Real impl will route to telemetry/alerting; for now swallow
            # so the pipeline result/raise reaches the caller untouched.
            pass
