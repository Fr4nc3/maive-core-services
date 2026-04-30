# MAIVE Ollama Edge Protector

> **Off by default.** Only used when a deployed or remote component must reach
> the researcher's local Ollama through a temporary protected tunnel. MAIVE's
> default no-budget runtime is direct local/self-hosted Ollama; Azure AI Foundry
> remains optional for paid cloud runs.

## What it does

A small FastAPI shim sitting in front of a local Ollama (`http://localhost:11434`)
that exposes:

- `POST /v1/chat` → forwards to Ollama `/api/chat`
- `POST /v1/embeddings` → forwards to Ollama `/api/embed`
- `GET  /healthz` → liveness

with two layers of protection:

1. **Bearer token** — `Authorization: Bearer <EDGE_PROTECTOR_TOKEN>`
2. **IP allowlist** — `EDGE_PROTECTOR_ALLOWLIST=127.0.0.1,::1` (comma-separated; honours `X-Forwarded-For` first hop)

All authenticated calls are logged to stdout (no PII).

## Run locally

```pwsh
cd src\edge-protector
uv sync
$env:EDGE_PROTECTOR_TOKEN     = "your-strong-random-token-here"
$env:EDGE_PROTECTOR_ALLOWLIST = "203.0.113.5"
$env:OLLAMA_BASE_URL          = "http://localhost:11434"
uv run uvicorn app:app --host 0.0.0.0 --port 8088
```

## Expose to the internet (researcher debugging only)

Use a tunnel — never open the port directly to the internet.

```pwsh
# Cloudflare Tunnel example (requires `cloudflared` installed)
cloudflared tunnel --url http://localhost:8088
```

Then in the cloud-hosted component, point `OLLAMA_BASE_URL` at the tunnel URL
and include the bearer token via your HTTP client.

## Smoke test

```pwsh
$token = $env:EDGE_PROTECTOR_TOKEN
curl -H "Authorization: Bearer $token" http://localhost:8088/healthz
# → {"status":"ok"}

curl -H "Authorization: Bearer wrong" http://localhost:8088/healthz
# → 401 Unauthorized
```

## Hard rules

- **Never** check the token into git or `.env.example`.
- **Never** expose this proxy without a deliberate short-lived tunnel and token.
- Prefer direct local Ollama for local/self-hosted runtime; use Azure AI Foundry only when choosing paid cloud resources.
- Tear the tunnel down when debugging is finished.
