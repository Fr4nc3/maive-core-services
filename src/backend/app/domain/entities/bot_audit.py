"""Append-only audit row for /api/bot/ask (DEC-013/019).

Pillar: Stable Core
Phase: R
Purpose: Append-only audit row for /api/bot/ask (DEC-013/019).
Documented in: docs/rai-policy.md#bot_audit
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class BotAudit(BaseModel):
    """Immutable audit row for one bot pipeline invocation.

    One row per /api/bot/ask call (both AI and static paths).
    Partition key in Cosmos: /session_id.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    request_ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    response_ts: datetime | None = None

    # Query fingerprint — never store raw text
    query_hash: str = ""  # sha256 hex
    query_length: int = 0
    language: str = "en"

    # Per-stage results
    bot_path: str = "ai"  # "ai" | "static"
    input_validator_pass: bool = True
    input_validator_reason: str = ""
    topic_gate_pass: bool = True
    topic_gate_score: float = 0.0
    prompt_injection_score: float = 0.0
    prompt_injection_blocked: bool = False
    system_prompt_id: str = ""
    output_validator_pass: bool = True
    output_validator_reasons: list[str] = Field(default_factory=list)

    # Telemetry
    latency_ms: int = 0
    llm_provider: str = ""
    llm_model: str = ""
    error_code: str | None = None  # set when a stage short-circuits

    # Client context (no PII)
    client_platform: str = ""
    client_version: str = ""
