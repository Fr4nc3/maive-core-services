"""Health check endpoints for Cosmos DB and LLM provider connectivity.

Pillar: Stable Core
Phase: B
Purpose: FastAPI route; Clean Architecture API boundary.
Documented in: plan/architecture.md
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from azure.core.exceptions import AzureError
from fastapi import APIRouter

from app.config import settings
from app.dependencies import get_llm_provider
from app.infrastructure.ai.llm_provider import ChatMessage
from app.infrastructure.persistence.cosmos_db.client import get_cosmos_client

router = APIRouter()


async def _check_cosmos() -> dict[str, Any]:
    """Lightweight Cosmos DB connectivity check."""
    try:
        client = get_cosmos_client()
        # Listing databases is a cheap account-level call.
        list(client.list_databases())
        return {"ok": True}
    except (AzureError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}


async def _check_llm() -> dict[str, Any]:
    """Ping the configured LLM provider with a tiny prompt."""
    started = time.perf_counter()
    try:
        provider = get_llm_provider()
        reply = await provider.chat(
            messages=[ChatMessage(role="user", content="ping")],
            max_tokens=4,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "ok": True,
            "provider": settings.llm_provider,
            "model": _current_model(),
            "latency_ms": latency_ms,
            "sample": reply.content[:80],
        }
    except (AzureError, httpx.HTTPError, ValueError) as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "ok": False,
            "provider": settings.llm_provider,
            "model": _current_model(),
            "latency_ms": latency_ms,
            "error": str(exc),
        }


def _current_model() -> str:
    return {
        "ollama": settings.ollama_chat_model,
        "azure": settings.azure_openai_chat_deployment,
    }.get(settings.llm_provider, "unknown")


@router.get("")
async def health() -> dict[str, Any]:
    """Composite health check: Cosmos DB + LLM provider."""
    cosmos = await _check_cosmos()
    llm = await _check_llm()
    overall = "ok" if cosmos["ok"] and llm["ok"] else "degraded"
    return {
        "status": overall,
        "cosmos": cosmos,
        "llm": {k: v for k, v in llm.items() if k != "sample"},
    }


@router.get("/llm")
async def health_llm() -> dict[str, Any]:
    """Detailed LLM provider check (latency + sample response)."""
    return await _check_llm()


@router.get("/cosmos")
async def health_cosmos() -> dict[str, Any]:
    """Detailed Cosmos DB connectivity check."""
    return await _check_cosmos()
