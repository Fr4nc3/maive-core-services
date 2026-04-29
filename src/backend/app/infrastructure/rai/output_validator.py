"""RAI guardrail (6-stage bot pipeline, DEC-019).

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""

import re

from app.infrastructure.rai import topic_gate
from app.infrastructure.rai.errors import BotPipelineError

# Crude PII detectors — emails, US-style phones, IPv4. We do NOT try to
# detect names; we only block obvious PII echoes.
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE_RE = re.compile(r"\b\d{3}[\s.-]\d{3}[\s.-]\d{4}\b")
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_URL_RE = re.compile(r"https?://\S+", re.I)

_LEAK_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsystem\s+prompt\b", re.I),
    re.compile(r"\bmy\s+instructions?\b", re.I),
    re.compile(r"\bmis\s+instrucciones\b", re.I),
    re.compile(r"\bI\s+was\s+told\s+to\b", re.I),
)


def validate(text: str) -> tuple[bool, list[str]]:
    """Return (pass, reasons). Does not raise — caller decides."""
    reasons: list[str] = []
    if not text or not text.strip():
        return False, ["empty_output"]
    if _EMAIL_RE.search(text):
        reasons.append("pii_email")
    if _PHONE_RE.search(text):
        reasons.append("pii_phone")
    if _IPV4_RE.search(text):
        reasons.append("pii_ip")
    if _URL_RE.search(text):
        reasons.append("url_leak")
    for pat in _LEAK_PATTERNS:
        if pat.search(text):
            reasons.append("instruction_leak")
            break
    if topic_gate.score(text) < topic_gate.MIN_SCORE:
        reasons.append("off_topic_output")
    return (not reasons), reasons


def check(text: str) -> tuple[bool, list[str]]:
    """Validate; raise BotPipelineError(502) if blocked. Returns (True, [])."""
    ok, reasons = validate(text)
    if not ok:
        raise BotPipelineError(
            stage="output_validator",
            reason=",".join(reasons),
            http_status=502,
            public_detail="output_blocked",
        )
    return True, []
