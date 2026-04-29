"""RAI guardrail (6-stage bot pipeline, DEC-019).

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.entities.bot_audit import BotAudit


def query_hash(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


@dataclass
class AuditDraft:
    session_id: str
    student_id: str
    language: str = "en"
    bot_path: str = "ai"  # "ai" | "static"
    client_platform: str = ""
    client_version: str = ""
    request_ts: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Mutated by the pipeline as stages run
    query_hash: str = ""
    query_length: int = 0
    input_validator_pass: bool = True
    input_validator_reason: str = ""
    topic_gate_pass: bool = True
    topic_gate_score: float = 0.0
    prompt_injection_score: float = 0.0
    prompt_injection_blocked: bool = False
    system_prompt_id: str = ""
    output_validator_pass: bool = True
    output_validator_reasons: list[str] = field(default_factory=list)
    llm_provider: str = ""
    llm_model: str = ""
    error_code: str | None = None

    def set_query(self, query: str) -> None:
        self.query_hash = query_hash(query)
        self.query_length = len(query)

    def to_audit(self) -> BotAudit:
        return BotAudit(
            session_id=self.session_id,
            student_id=self.student_id,
            request_ts=self.request_ts,
            response_ts=datetime.now(UTC),
            query_hash=self.query_hash,
            query_length=self.query_length,
            language=self.language,
            bot_path=self.bot_path,
            input_validator_pass=self.input_validator_pass,
            input_validator_reason=self.input_validator_reason,
            topic_gate_pass=self.topic_gate_pass,
            topic_gate_score=self.topic_gate_score,
            prompt_injection_score=self.prompt_injection_score,
            prompt_injection_blocked=self.prompt_injection_blocked,
            system_prompt_id=self.system_prompt_id,
            output_validator_pass=self.output_validator_pass,
            output_validator_reasons=list(self.output_validator_reasons),
            latency_ms=int(
                (datetime.now(UTC) - self.request_ts).total_seconds() * 1000
            ),
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            error_code=self.error_code,
            client_platform=self.client_platform,
            client_version=self.client_version,
        )
