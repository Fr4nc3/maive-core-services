"""Typed pipeline error so each stage can short-circuit cleanly.

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""


class BotPipelineError(Exception):
    """Raised by any guardrail stage to short-circuit the pipeline."""

    def __init__(
        self,
        stage: str,
        reason: str,
        http_status: int = 422,
        public_detail: str = "",
    ) -> None:
        self.stage = stage
        self.reason = reason
        self.http_status = http_status
        # public_detail is what the client sees; reason is for the audit row
        self.public_detail = public_detail or stage
        super().__init__(f"[{stage}] {reason}")
