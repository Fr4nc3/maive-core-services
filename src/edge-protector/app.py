# Documented in: src/edge-protector/README.md, docs/decisions.md (DEC-017)
"""MAIVE Edge Protector — bearer-token + IP-allowlisted Ollama shim.

NOT used by the experiment runtime. Researcher debugging only.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request, status

logger = logging.getLogger("edge-protector")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TOKEN = os.environ.get("EDGE_PROTECTOR_TOKEN", "")
ALLOWLIST = {
    ip.strip()
    for ip in os.environ.get("EDGE_PROTECTOR_ALLOWLIST", "127.0.0.1,::1").split(",")
    if ip.strip()
}
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
TIMEOUT = float(os.environ.get("EDGE_PROTECTOR_TIMEOUT", "120"))

app = FastAPI(title="MAIVE Edge Protector", version="0.1.0")


def _client_ip(request: Request) -> str:
    # Honour X-Forwarded-For when behind a tunnel; first hop wins.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",", 1)[0].strip()
    return request.client.host if request.client else ""


def _check(request: Request, authorization: str | None) -> None:
    if not TOKEN:
        logger.error("EDGE_PROTECTOR_TOKEN is not set; refusing all requests")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="not configured")
    expected = f"Bearer {TOKEN}"
    if authorization != expected:
        logger.warning("auth fail from %s", _client_ip(request))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad token")
    ip = _client_ip(request)
    if ip not in ALLOWLIST:
        logger.warning("ip not allowlisted: %s", ip)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ip not allowlisted")


async def _forward(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{OLLAMA_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat")
async def chat(
    payload: dict[str, Any],
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _check(request, authorization)
    logger.info("chat from %s model=%s", _client_ip(request), payload.get("model"))
    return await _forward("/api/chat", payload)


@app.post("/v1/embeddings")
async def embeddings(
    payload: dict[str, Any],
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _check(request, authorization)
    logger.info("embed from %s model=%s", _client_ip(request), payload.get("model"))
    return await _forward("/api/embed", payload)
