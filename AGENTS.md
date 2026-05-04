# MAIVE Core Services — Agent Brief

> **Always-loaded context** for any AI agent (Copilot, Claude, etc.) working in this repository.

## What this project is

**MAIVE** (Mentor-Agent Immersive VR for Education) is a PhD thesis serious game for astronomy education. It is a **multi-agent AI-driven adaptive VR platform** evaluated against a non-adaptive VR control condition across three research questions:

- **RQ1** — Conceptual learning gains (concept-inventory pre/post)
- **RQ2** — Engagement and attitudes (ARCS + telemetry)
- **RQ3** — Problem-solving and conceptual transfer

PhD owner: Francia F. Riesco. Thesis source-of-truth: [docs/PhD-Astronomy World - Work In progress- francia-riesco.md](docs/PhD-Astronomy%20World%20-%20Work%20In%20progress-%20francia-riesco.md).

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 · FastAPI · UV · pydantic-settings |
| Database | Azure Cosmos DB (NoSQL) + DiskANN vector index |
| AI | Multi-agent (4 agents) · LLM Provider abstraction (Ollama default local/self-hosted, Azure AI Foundry optional) |
| Frontend | React 18 · TypeScript · Vite · react-router-dom |
| VR Clients | Spatial.io · VRChat · Unity single-player · Web (flat) |
| Cloud | Azure (App Service, Functions, Monitor) |

## Architecture rule (Clean Architecture)

```
API (FastAPI routes) → Application (DTOs, Use Cases) → Domain (Entities, Interfaces) → Infrastructure (Cosmos DB, AI)
```

**Inner layers never depend on outer layers.** Domain has zero external dependencies.

When adding a new feature, follow this order:
1. Domain entity
2. Repository interface (port)
3. DTO (Create / Update / Response)
4. Use case
5. Cosmos repository implementation
6. API route
7. Wire in `app/dependencies.py`
8. Append a `DEC-NNN` entry to [docs/decisions.md](docs/decisions.md)
9. Add a paragraph to the relevant section in [docs/paper/maive-systems-engineering-extended.md](docs/paper/maive-systems-engineering-extended.md)

## Identity rule (the 5-platform model)

Every API call from a VR or web client carries:
- `platform ∈ {"spatial.io", "vrchat", "sinespace", "unity", "web"}`
- `platform_user_id` — the user identifier on that platform

The backend issues a stable internal `user.id` (UUID) on first contact via `POST /api/users/identify` and reuses it on every subsequent call.

## Unified bot rule

All clients call **`POST /api/bot/ask`** with the same payload. The backend inspects `session.condition` to route:

- `condition = "non-adaptive-vr"` → static `help_content` lookup (control group)
- `condition = "maive"` → multi-agent adaptive AI pipeline

**Never bypass `/api/bot/ask` from a client.** Same payload across web, Unity, Spatial.io, VRChat.

## LLM provider rule

All agent code uses the abstract `LLMProvider` interface. Switching is **config-only** via `LLM_PROVIDER` env var. Ollama is the default budget-conscious runtime for local and production-development use on the researcher's own hardware; Azure AI Foundry is an optional paid cloud provider when budget is available.

- `ollama` -> default local/self-hosted runtime (httpx -> Ollama REST API)
- `azure` -> optional paid cloud runtime (openai SDK -> Azure AI Foundry)

Agents never import a provider class directly.

## Living documentation

| File | Purpose |
|---|---|
| [docs/plan.md](docs/plan.md) | Current project plan, phases, sequencing |
| [docs/plan-template.md](docs/plan-template.md) | Strict template every new phase MUST follow (Pillar / Goal / Owner / Status) |
| [docs/plan-history.md](docs/plan-history.md) | Append-only log of plan restructures. **Every restructure adds a row.** |
| [docs/status.md](docs/status.md) | Running status board: current sprint, blockers, weekly changelog |
| [docs/decisions.md](docs/decisions.md) | Architectural decisions (DEC-NNN), reverse chronological |
| [plan/architecture.md](plan/architecture.md) | Architecture spec (entities, endpoints, containers) |
| [plan/telemetry-model.md](plan/telemetry-model.md) | Telemetry event types and payloads |
| [docs/paper/maive-systems-engineering-extended.md](docs/paper/maive-systems-engineering-extended.md) | Internal extended systems-engineering paper (long form) |
| [docs/paper/maive-systems-engineering-publishable.md](docs/paper/maive-systems-engineering-publishable.md) | Publishable derivative (built after data collection) |

## Rules of engagement (for any agent working here)

1. **Read [docs/status.md](docs/status.md) first** to understand current focus and blockers.
2. **Follow Clean Architecture order** when adding features (see Architecture rule above).
3. **Append a DEC-NNN entry** to [docs/decisions.md](docs/decisions.md) for any architectural choice — date, status, rationale.
4. **Update [docs/status.md](docs/status.md)** with a one-line entry under "What changed this week" after merging meaningful work.
5. **Cross-reference the extended paper** — when shipping a backend change, add a `# Documented in: docs/paper/maive-systems-engineering-extended.md#section` comment near the top of the changed file, and add at least one paragraph to that section.
6. **Run `cd src/backend && uv run ruff check .`** before declaring backend work complete. Must exit 0.
7. **Never create new repository implementations without inheriting from `BaseCosmosRepository`** (see `app/infrastructure/persistence/cosmos_db/base_repository.py`).
8. **Never create client-specific endpoints** — all VR/web clients hit the same routes with `platform` discriminator.
9. **No PII** — users are identified only by `(platform, platform_user_id)` and an internal UUID. No email, no real name (use optional `display_name` only).
10. **No Azure service keys** — never add API keys, tokens, credentials, or Azure service key fields to code/config. Use `Settings` for non-secret configuration and Azure credentials/RBAC for Cosmos DB and Azure AI Foundry auth.
11. **Treat the thesis document as authoritative** for research questions, hypotheses, and statistical decision rules — do not invent new ones.

## Common commands

```powershell
# Backend
cd src/backend
uv sync
uv run uvicorn app.main:app --reload
uv run ruff check .
uv run pytest -v

# Frontend
cd src/frontend
npm install
npm run dev
npm run build

# NASA RAG ingestion (Ollama default)
cd src/backend
uv run python -m app.cli.ingest_knowledge --provider ollama

# Static help content seeding (TBD)
uv run python -m app.cli.seed_help_content
```

## Out of scope (until further notice)

- Production deployment automation
- Entra ID / OAuth authentication (consented research only for now)
- Mobile-native VR clients (Unity SDK is desktop-PCVR only initially)

---

*This file is loaded automatically by GitHub Copilot and Claude. Keep it under ~5 KB. Detailed rules go in [.github/instructions/](.github/instructions/).*
