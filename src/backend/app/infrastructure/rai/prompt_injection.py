"""RAI guardrail (6-stage bot pipeline, DEC-019).

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""

import re

from app.infrastructure.rai.errors import BotPipelineError

# Each pattern contributes its weight to the score (capped at 1.0).
_PATTERNS: tuple[tuple[re.Pattern[str], float], ...] = (
    (re.compile(r"\bignore\s+(all\s+)?previous\b", re.I), 0.6),
    (re.compile(r"\bignore\s+(all\s+)?prior\b", re.I), 0.6),
    (re.compile(r"\bdisregard\s+(the\s+)?(above|previous)\b", re.I), 0.6),
    (re.compile(r"\bforget\s+(everything|all\s+instructions)\b", re.I), 0.5),
    (re.compile(r"\bsystem\s*:\s*", re.I), 0.5),
    (re.compile(r"\bassistant\s*:\s*", re.I), 0.3),
    (re.compile(r"\byou\s+are\s+now\b", re.I), 0.4),
    (re.compile(r"\bnew\s+instructions?\b", re.I), 0.3),
    (re.compile(r"\boverride\s+(your|the)\b", re.I), 0.4),
    (re.compile(r"<\s*/?\s*(system|prompt|instructions?)\s*>", re.I), 0.6),
    (re.compile(r"\b(jailbreak|dan\s+mode|developer\s+mode)\b", re.I), 0.7),
    (
        re.compile(
            r"\b(reveal|print|repeat|leak)\s+(your|the)\s+"
            r"(prompt|system\s+prompt|instructions?)\b",
            re.I,
        ),
        0.7,
    ),
    (re.compile(r"```+\s*(system|prompt)", re.I), 0.5),
    # Spanish equivalents
    (re.compile(r"\bignora\s+(las\s+)?instrucciones\s+(anteriores|previas)\b", re.I), 0.6),
    (re.compile(r"\bolvida\s+(todo|las\s+instrucciones)\b", re.I), 0.5),
    (re.compile(r"\beres\s+ahora\b", re.I), 0.4),
)

BLOCK_THRESHOLD = 0.5


def score(text: str) -> float:
    """Return a 0..1 injection-suspicion score."""
    if not text:
        return 0.0
    total = 0.0
    for pat, weight in _PATTERNS:
        if pat.search(text):
            total += weight
    return min(1.0, total)


def check(text: str) -> float:
    """Return the score; raise BotPipelineError(403) if blocked."""
    s = score(text)
    if s >= BLOCK_THRESHOLD:
        raise BotPipelineError(
            stage="prompt_injection",
            reason=f"score={s:.3f}",
            http_status=403,
            public_detail="blocked",
        )
    return s
