"""RAI guardrail (6-stage bot pipeline, DEC-019).

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""

import unicodedata

from app.infrastructure.rai.errors import BotPipelineError

MAX_QUERY_LENGTH = 2000
ALLOWED_LANGUAGES = frozenset({"en", "es"})

# Strip control chars except common whitespace (\t \n \r)
_KEEP_CONTROL = frozenset({"\t", "\n", "\r"})


def _strip_control(s: str) -> str:
    return "".join(
        c for c in s if c in _KEEP_CONTROL or unicodedata.category(c)[0] != "C"
    )


def validate(query: str, language: str) -> str:
    """Return the cleaned query, or raise BotPipelineError."""
    if language not in ALLOWED_LANGUAGES:
        raise BotPipelineError(
            stage="input_validator",
            reason=f"language_not_allowed:{language}",
            http_status=422,
            public_detail="language_not_allowed",
        )
    if not isinstance(query, str):
        raise BotPipelineError(
            stage="input_validator",
            reason="query_not_string",
            http_status=422,
            public_detail="input_invalid",
        )
    cleaned = unicodedata.normalize("NFC", query)
    cleaned = _strip_control(cleaned).strip()
    if not cleaned:
        raise BotPipelineError(
            stage="input_validator",
            reason="empty_query",
            http_status=422,
            public_detail="empty_query",
        )
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise BotPipelineError(
            stage="input_validator",
            reason=f"too_long:{len(cleaned)}",
            http_status=422,
            public_detail="query_too_long",
        )
    return cleaned
