from fastapi import APIRouter

from app.infrastructure.agents.adaptive_agent import AdaptiveAgent

router = APIRouter()


@router.post("/adapt")
async def request_adaptation(session_id: str):
    agent = AdaptiveAgent()
    result = await agent.evaluate_session(session_id)
    return result
