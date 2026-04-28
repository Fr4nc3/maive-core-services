"""
Unified bot endpoint.

Both the static (control-group) bot and the AI agentic bot use the same
request/response contract.  The backend inspects the session's ``condition``
to decide which path to take:

* ``non-adaptive-vr`` → static help-content lookup
* ``maive``           → full multi-agent AI pipeline
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.application.dtos.help_content_dtos import HelpQueryDTO
from app.application.use_cases.help_content_use_cases import GetHelpForContextUseCase
from app.dependencies import (
    get_coordination_agent,
    get_help_content_repository,
    get_session_repository,
    get_student_repository,
)

router = APIRouter()


# ── Shared request / response DTOs ──────────────────────────────────────

class BotAskRequest(BaseModel):
    """Unified request sent by Unity for *any* bot interaction."""

    session_id: str
    planet: str
    section: str = ""
    query: str = ""  # free-text question from the student
    content_topic: str = ""
    difficulty_level: str = ""
    help_type: str = "explanation"  # "hint" | "explanation" | "scaffold" | "encouragement"
    language: str | None = None  # "en" | "es" | None — see DEC-014 for resolution order


class BotAskResponse(BaseModel):
    """Unified response returned to Unity regardless of bot type."""

    bot_type: str  # "hardcoded" | "ai"
    action_type: str  # "hint" | "explanation" | "scaffold" | "encouragement" | "no_action"
    title: str = ""
    body_text: str = ""
    media_url: str | None = None
    source: str = ""  # e.g. NASA source title or "static-content"
    follow_up_question: str = ""
    confidence: float = 1.0
    difficulty_from: str = ""
    difficulty_to: str = ""
    language: str = "en"  # resolved language actually used for this response (DEC-014)
    language_fallback: bool = False  # True when target-language content was unavailable


# ── Endpoint ────────────────────────────────────────────────────────────

@router.post("/ask", response_model=BotAskResponse)
async def bot_ask(body: BotAskRequest):
    """
    Single entry-point for bot help.

    Unity sends the same payload for both experimental conditions.
    The backend routes to static content or the AI agent pipeline
    based on the session's ``condition`` field.
    """
    session_repo = get_session_repository()
    session = await session_repo.get_by_id(body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    language = await _resolve_language(body, session)

    if session.condition == "non-adaptive-vr":
        return await _static_bot_response(body, language)
    else:
        return await _ai_bot_response(body, session, language)


async def _resolve_language(body: BotAskRequest, session) -> str:
    """Effective-language resolution per DEC-014.

    Order: request override → session.language → student.preferred_language → "en".
    """
    if body.language:
        return body.language
    if getattr(session, "language", None):
        return session.language
    student_repo = get_student_repository()
    student = await student_repo.get_by_id(session.student_id)
    if student is not None and getattr(student, "preferred_language", None):
        return student.preferred_language
    return "en"


# ── Static (control-group) path ─────────────────────────────────────────

async def _static_bot_response(body: BotAskRequest, language: str) -> BotAskResponse:
    repo = get_help_content_repository()
    use_case = GetHelpForContextUseCase(repo)

    items = await use_case.execute(
        HelpQueryDTO(
            planet=body.planet,
            section=body.section or None,
            content_topic=body.content_topic or None,
            difficulty_level=body.difficulty_level or None,
            help_type=body.help_type or None,
            limit=1,
        )
    )
    # NOTE: Phase N5 will add `language` filtering to HelpQueryDTO + the
    # Cosmos query so the static path returns the language-matched row.
    # For now the row is returned as-is and `language` is echoed back so
    # the client knows what language was resolved.

    if not items:
        return BotAskResponse(
            bot_type="hardcoded",
            action_type="no_action",
            body_text="No help content available for this context.",
            language=language,
        )

    item = items[0]
    return BotAskResponse(
        bot_type="hardcoded",
        action_type=item.help_type or "explanation",
        title=item.title,
        body_text=item.body_text,
        media_url=item.media_url,
        source="static-content",
        confidence=1.0,
        language=language,
    )


# ── AI agentic path ─────────────────────────────────────────────────────

async def _ai_bot_response(body: BotAskRequest, session, language: str) -> BotAskResponse:
    agent = get_coordination_agent()
    query = body.query or body.content_topic or body.section or "general help"
    # NOTE: Phase N4 + N6 will pass `language` into the coordination agent
    # so the multi-agent pipeline picks the matching system prompt and
    # filters RAG retrieval. For now the language is resolved + echoed
    # back so clients can render correctly even before agent translation
    # lands.
    result = await agent.evaluate_session(body.session_id, help_query=query)

    return BotAskResponse(
        bot_type="ai",
        action_type=result.get("action_type", "no_action"),
        body_text=result.get("content", ""),
        source=result.get("trigger_reason", ""),
        confidence=result.get("confidence", 0.0),
        difficulty_from=result.get("difficulty_from", ""),
        difficulty_to=result.get("difficulty_to", ""),
        follow_up_question="",
        language=language,
    )
