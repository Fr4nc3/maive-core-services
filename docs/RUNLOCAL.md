# Run MAIVE Core Services Locally

> Single source of truth for booting the full MAIVE stack on your laptop.
> Two paths: **A — direct `.venv` (fastest dev loop)**, **B — Docker Compose (parity with prod)**.
> Cross-references: [architecture](../plan/architecture.md) · [decisions](decisions.md) · [QA](qa/qa-checklist.md).

## Prerequisites

| Tool | Version | Why | Install |
|---|---|---|---|
| Python | 3.12+ | Backend runtime | <https://python.org> |
| `uv` | 0.5+ | Python package manager (replaces pip+venv) | `pip install uv` or `winget install astral-sh.uv` |
| Node.js | 20+ | Frontend tooling | <https://nodejs.org> |
| Ollama | latest | Local LLM (`LLM_PROVIDER=ollama`) | <https://ollama.com> |
| Docker Desktop | 4.30+ | **Path B only** + Cosmos emulator | <https://www.docker.com/products/docker-desktop> |
| Azure Cosmos DB Emulator | vnext-preview (Linux container) | Local persistence | `docker pull mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview` |
| ripgrep (`rg`) | optional | Faster `qa_audit if-else-scan` (Python fallback exists) | `winget install BurntSushi.ripgrep.MSVC` |

### One-time Ollama models
```pwsh
ollama pull llama3
ollama pull nomic-embed-text
```

### `.env` setup
Copy `src/backend/.env.example` (or root `.env.example` once Q6 lands) to `src/backend/.env`. Sign in with `az login` or `azd auth login` so the backend can use Azure credentials for Cosmos DB. Minimum for local:
```dotenv
APP_ENV=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
COSMOS_ENDPOINT=https://<your-account>.documents.azure.com:443/
COSMOS_DATABASE=maive
```
The default local path uses Azure credential/RBAC auth. The Cosmos emulator key-based path is off-default and should only be used with an explicit local-emulator exception.

---

## Path A — Direct `.venv` (recommended for development)

Fastest inner loop: backend hot-reloads on save, frontend HMR via Vite.

### 1. Start Ollama
```pwsh
# Native (recommended)
ollama serve   # usually auto-started on Windows
```

### 2. Start the Cosmos DB Emulator
```pwsh
docker run -d --name maive-cosmos -p 8081:8081 -p 10250-10255:10250-10255 `
  -e AZURE_COSMOS_EMULATOR_PARTITION_COUNT=10 `
  -e AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE=true `
  mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview
```
Wait ~30 s, then trust the cert: <https://localhost:8081/_explorer/index.html>.

### 3. Backend
```pwsh
cd src\backend
uv sync                    # install deps (one-time / on lock changes)
uv run uvicorn app.main:app --reload --port 8000
```
Health check: <http://localhost:8000/api/health>

### 4. Frontend
```pwsh
cd src\frontend
npm install                # one-time / on package.json changes
npm run dev                # Vite dev server, default http://localhost:5173
```

### 5. Smoke test
```pwsh
# Identify a learner
curl -X POST http://localhost:8000/api/users/identify `
  -H "Content-Type: application/json" `
  -d '{\"platform\":\"web\",\"platform_user_id\":\"smoke-test-1\",\"display_name\":\"Smoke Tester\",\"preferred_language\":\"en\"}'

# Create a session
curl -X POST http://localhost:8000/api/sessions `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":\"<id-from-step-1>\",\"condition\":\"control\",\"difficulty_level\":\"easy\"}'

# Ask the bot
curl -X POST http://localhost:8000/api/sessions/<session-id>/ask `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"What is the closest planet to the Sun?\"}'
```

### 6. Run the QA gate before pushing
```pwsh
cd src\backend
uv run python -m app.cli.qa_audit all
```

---

## Path B — Docker Compose (production parity)

Boots backend + frontend + Cosmos emulator (+ optionally Ollama) in one command.

```pwsh
docker compose up -d
```

Services exposed:

| Service | URL | Notes |
|---|---|---|
| frontend | <http://localhost:5173> | nginx-served Vite build, proxies `/api/*` to backend |
| backend | <http://localhost:8000/api/health> | Containerized FastAPI |
| cosmos | <https://localhost:8081/_explorer/index.html> | Emulator |
| ollama | <http://localhost:11434> | **Recommended:** run Ollama natively (GPU, faster) and set `OLLAMA_BASE_URL=http://host.docker.internal:11434` in `.env` |

Tear down:
```pwsh
docker compose down                 # keep volumes
docker compose down -v              # nuke volumes (resets Cosmos data)
```

Rebuild after code changes:
```pwsh
docker compose up -d --build
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cosmos emulator cert untrusted` | Visit <https://localhost:8081/_explorer/index.html> in your browser and accept the self-signed cert (Windows trusts it for the session). For permanent trust, install via `Import-Certificate`. |
| `connection refused` to Ollama from a container | Use `host.docker.internal` instead of `localhost` in `OLLAMA_BASE_URL`. |
| `npm install` slow on Windows | Enable Developer Mode + use the same drive as the project (no junctioned paths). |
| `uv sync` fails on Windows + long paths | Run `git config --system core.longpaths true`. |
| Frontend cannot reach backend | Check `vite.config.ts` proxy or, in Path B, that nginx `BACKEND_URL` env points to `http://backend:8000`. |

---

## What's NOT covered here

- **Cloud deployment** → see [deployment/runbook.md](deployment/runbook.md) (Phase Q6/Q9)
- **Edge Protector for cloud → local Ollama** → see [DEC-017](decisions.md) and `src/edge-protector/` (Phase Q5)
- **CI/CD** → `.github/workflows/` (Phase Q7)
- **Dev Containers** → intentionally **not supported** (Path A is simpler; Path B is closer to prod)
