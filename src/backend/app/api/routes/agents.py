"""FastAPI route; Clean Architecture API boundary.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.dependencies import get_coordination_agent

router = APIRouter()


class AdaptRequest(BaseModel):
    session_id: str
    help_query: str | None = None


@router.post("/adapt")
async def request_adaptation(body: AdaptRequest):
    """Run the multi-agent adaptive pipeline (optionally with a help query)."""
    agent = get_coordination_agent()
    return await agent.evaluate_session(body.session_id, body.help_query)
