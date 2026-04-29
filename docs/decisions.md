# MAIVE — Decision Log

All architectural and design decisions for the MAIVE platform, in reverse chronological order.

---

## DEC-020 — Granular sub-agent surface (`@maive-deploy`, `@maive-frontend`, `@maive-research`)

**Date:** 2026-04-29
**Status:** Accepted

Split the previously-monolithic `@maive-lead` surface into a top-level
dispatcher (`.github/copilot-instructions.md`) plus four owners:

- `@maive-rai` — bot pipeline & RAI guardrails (DEC-019)
- `@maive-deploy` — Azure infra, Bicep, containers, Key Vault, MI/RBAC
- `@maive-frontend` — React + TS + i18n + nginx
- `@maive-research` — thesis methodology, RQ1/RQ2/RQ3, paper updates

`@maive-lead` remains as a router for cross-cutting work; `@maive-qa` remains
read-only. Each agent has an `applyTo`-scoped instruction file under
`.github/instructions/`. Rationale: smaller blast radius per turn, clearer
hard-rule sets, easier QA enforcement of who-touches-what.

## DEC-019 — RAI Bot Pipeline (6 stages + immutable audit)

**Date:** 2026-04-29
**Status:** Accepted
**Builds on:** DEC-012 (RAI baseline), DEC-013 (audit immutability)

Every call to `POST /api/bot/ask` traverses a fixed 6-stage pipeline,
regardless of `session.condition`:

```
input_validator → topic_gate → prompt_injection → system_prompt
  → CoordinationAgent.evaluate_session → output_validator → audit
```

Implemented in `src/backend/app/infrastructure/rai/`. Orchestrated by
`BotPipelineUseCase` (`src/backend/app/application/use_cases/bot_pipeline_use_case.py`).
HTTP status mapping: input/topic = 422, injection = 403, output = 502, LLM = 503.

**Immutability rules:**
- `BotAuditRepository` interface has no `update`/`delete`.
- The audit row is the only place per-request RAI evidence is recorded.
- Raw query is never stored — only `sha256(query)` + length.
- Raw LLM output is never stored — only block reasons.

**Container:** `bot_audit` declared explicitly in `infra/modules/cosmos.bicep`
with partition key `/session_id`.

**Best-effort:** the audit write sits in a `finally` block and **never**
breaks the request (DEC-019 invariant). The two `except Exception` blocks
in `bot_pipeline_use_case.py` and `routes/bot.py` are sanctioned by this
DEC and excluded from the `qa_audit` bare-except scan.

**Test gate:** `tests/rai/` — 42 tests covering each stage + 5 integration
tests with `FakeAgent` + in-memory audit repo. CI gate: green.

**Documentation:** [docs/rai-policy.md](rai-policy.md),
[docs/threat-model.md](threat-model.md). QA enforced by
`uv run python -m app.cli.qa_audit rai-check`.

## DEC-018 — Container deployment topology: AppSvc (frontend) → Container Apps (backend)

**Date:** 2026-04-28
**Status:** Accepted

Deploy MAIVE Core Services to Azure with the following topology, mirroring
`microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator` and
`microsoft/content-generation-solution-accelerator`:

- **Frontend** — Azure App Service (Linux, B1) running `nginx:alpine` container.
  Reverse-proxies `/api/*` to the backend FQDN; serves the Vite SPA otherwise.
- **Backend** — Azure Container Apps (single env, 1–3 replicas) running the
  FastAPI image from ACR. System-assigned managed identity authenticates to
  Cosmos, AI Foundry, and Key Vault.
- **Persistence** — Cosmos DB serverless (NoSQL) with vector-search capability.
- **LLM** — Azure AI Foundry account with `chat` + `embedding` deployments.
- **Secrets** — Key Vault (RBAC mode); MI grants only.
- **Observability** — Application Insights (workspace-based) + Log Analytics.
- **Tooling** — [`azure.yaml`](../azure.yaml) + [`infra/main.bicep`](../infra/main.bicep)
  drive deployment via `azd up`. CI in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml);
  manual deploy in [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)
  using GitHub OIDC federated credentials (no stored secrets).

**Why Container Apps not App Service for backend:** matches MACAE; gives us
autoscale + revisions; cleaner managed-identity story than ACI.
**Why App Service for frontend:** simpler than a second Container App for a
static-with-proxy workload; B1 is the cheapest tier with always-on.

**Out of scope (deferred):** Front Door + WAF, private endpoints / VNet,
Entra ID auth, multi-region. Future `azure_custom.yaml` variant per MACAE.

---

## DEC-017 — Cloud LLM = Azure AI Foundry; Ollama stays local; optional Edge Protector for debugging

**Date:** 2026-04-28
**Status:** Accepted

**Rule:** Production / cloud-deployed components run with `LLM_PROVIDER=azure`
against Azure AI Foundry. Ollama is **never** deployed to Azure. Local
development runs `LLM_PROVIDER=ollama` against the researcher's laptop.

**Edge Protector** — [`src/edge-protector/`](../src/edge-protector/) is a small
FastAPI shim that exposes a researcher's local Ollama via a token-protected,
IP-allowlisted HTTPS endpoint behind a Cloudflare Tunnel / dev tunnel. Used
**only** for ad-hoc debugging (e.g. comparing a cloud-hosted dashboard's
behaviour against a local model). **Never used by experiment runtime.**

**Files:**
- [`src/edge-protector/app.py`](../src/edge-protector/app.py) (FastAPI shim)
- [`src/edge-protector/README.md`](../src/edge-protector/README.md) (run instructions)

**Verification:** Without `Authorization: Bearer <token>`, every endpoint
returns 401. From a non-allowlisted IP, every endpoint returns 403.

---

## DEC-016 — `LLMProviderRegistry` for LLM backends; defer agent/repo registries

**Date:** 2026-04-28
**Status:** Accepted

Replace the if/elif provider switch in `app.dependencies.build_llm_provider`
and `app.api.routes.health._current_model` with a class-level
`LLMProviderRegistry`. Each provider self-registers via
`@LLMProviderRegistry.register("<key>")` at module import; `dependencies.py`
becomes one line: `LLMProviderRegistry.build(settings.llm_provider, settings)`.
`LLMProvider` gains a `model_name` property so `health.py` no longer needs to
branch on provider.

**Files:**
- NEW: [`src/backend/app/infrastructure/ai/registry.py`](../src/backend/app/infrastructure/ai/registry.py)
- MODIFIED: [`llm_provider.py`](../src/backend/app/infrastructure/ai/llm_provider.py)
  (added `model_name`), [`ollama_provider.py`](../src/backend/app/infrastructure/ai/ollama_provider.py)
  + [`azure_foundry_provider.py`](../src/backend/app/infrastructure/ai/azure_foundry_provider.py)
  (decorator + builder), [`dependencies.py`](../src/backend/app/dependencies.py),
  [`health.py`](../src/backend/app/api/routes/health.py)

**Verification:** `qa_audit if-else-scan` reports 0 hits for
`provider == "..."` and `elif.*provider`. Adding a new provider requires
zero edits to `dependencies.py`.

**Deferred (Phase P2/P3):** AgentRegistry and CosmosRepoRegistry are NOT
introduced now — the codebase has no if/elif branching there to remove.
`CoordinationAgent` is the single entry point for agents, and `_get_repo(cls)`
already behaves as a class-keyed registry. Will revisit if a 5th agent is
added or when multiple persistence backends ship.

---

## DEC-015 — QA agent + `qa_audit.py` is the canonical pre-PR gate

**Date:** 2026-04-28
**Status:** Accepted

Introduce a single read-only QA reviewer (`@maive-qa`) backed by a Python audit
runner ([`src/backend/app/cli/qa_audit.py`](../src/backend/app/cli/qa_audit.py))
and a 5-rubric checklist ([`docs/qa/qa-checklist.md`](qa/qa-checklist.md)).

**Five rubrics audited:**
1. Clean & modular (Clean Architecture order)
2. Dynamic & extensible (no `provider == "..."` outside registries)
3. Latest libraries (no Pydantic v1, no `datetime.utcnow`, deps current)
4. RAI implemented (DEC-012/013 evidence: `rai-policy.md`, `threat-model.md`,
   `bot_audit`, guardrail modules)
5. Factory / registry instead of if/else (Phase P)

**Boundaries:**
- Read-only by default. The `--fix` flag runs only `ruff --fix`, `ruff format`,
  and `prettier --write` — no hand-edits.
- NEVER touches `app/domain/entities/`, `docs/decisions.md`, `docs/plan.md`,
  `docs/paper/`, or `tests/`.
- Falls back to a Python regex scan when `ripgrep` is not installed (Windows-friendly).
- The agent definition is at [`.github/agents/maive-qa.agent.md`](../.github/agents/maive-qa.agent.md)
  and the encoded rules live in [`.github/instructions/maive-qa.instructions.md`](../.github/instructions/maive-qa.instructions.md).

**Why now:** before kicking off Phase P (factory/registry refactor), we need
a deterministic gate that proves each refactor is moving the needle on rubric
#5. The same gate also surfaces pre-existing items for Phase P (e.g.
`if settings.llm_provider == "ollama"` in `dependencies.py` and `health.py`,
`datetime.utcnow()` in two use cases, bare `except Exception` in three Cosmos
repos and the health route).

**Next:** Phase P uses `qa_audit if-else-scan` as its acceptance test.

---

## DEC-014 — Bilingual support model (English / Spanish)

**Date:** 2026-04-28
**Status:** Accepted

The MAIVE experience and service must respect a learner's preferred language (`en` or `es`) end-to-end: client UI, session record, static help content, NASA RAG retrieval, agent prompts, bot response, and telemetry/audit. Language is recorded as a research-grade variable so RQ1/RQ2/RQ3 analyses can be split by language.

**Resolution order (effective language for any bot/help call):**
1. `BotAskRequest.language` (per-request override)
2. `Session.language` (per-session override of user default)
3. `User.preferred_language` (set on `POST /api/users/identify`)
4. Default: `"en"`

**Translation discipline:**
- **Agent system prompts are human-translated** (`<agent>_en.md` + `<agent>_es.md`) — auditable and reproducible. No runtime machine translation.
- Spanish prompts and Spanish help content are authored by the PhD owner (Francia Riesco), who is bilingual. No third-party translation service in the loop.
- **Static help content** must exist in **both** languages before a planet/section is released for a Spanish session (enforced by seeder check, not at request time).
- **NASA RAG fallback rule:** if no chunks exist in the target language, retrieve English chunks but instruct the LLM to *answer in the target language*; mark the response with `language_fallback=true` for audit.
- **No machine-translation API dependency** in this phase (small dependency surface).

**Locale scope (v1):** `es` neutral (LatAm/EU-agnostic). Locale tag (`es-MX`, `es-ES`, `es-419`) deferred until pilot data shows confusion.

**Default at first contact:** all clients (web, Unity, VRChat, Spatial.io) default to `"en"` unless the learner explicitly selects Spanish via the in-experience language selector. Browser `Accept-Language` is **not** auto-applied (keeps behaviour consistent across the 5 platforms and avoids surprising the participant before the consent step).

**Research instruments:** the concept inventory and ARCS survey use **published validated Spanish versions only** (sourcing tracked by Francia). Freshly-translated instruments would be a research-validity threat (psychometric properties not preserved). Citations of the validated Spanish instruments will be added to the extended paper §10 (Evaluation Plan) and §References before data collection.

**Telemetry/audit:** every `telemetry_event` and (Phase J1) `bot_audit` row records the resolved `language` so per-language RQ analyses are trivial.

**Implementation:** see Phase N in [docs/plan.md](plan.md). Diagram: `docs/paper/figures/language-flow.md` (planned).

---

## DEC-013 — `bot_audit` Cosmos container is the canonical RAI/security evidence store

**Date:** 2026-04-28
**Status:** Proposed (placeholder — to be finalised by Phase J4)

A new Cosmos container `bot_audit` (partition `/session_id`) will record every bot interaction and every guardrail verdict, providing both (a) reproducible thesis evidence for RQ1/RQ2/RQ3 and (b) forensic trail for security/RAI audits.

**Schema (draft):** `id, session_id, user_id, timestamp, request_payload, response_payload, guardrail_verdicts[{stage, verdict, score, rule_hit}], provider, model, prompt_tokens, completion_tokens, latency_ms, condition`.

**Linkage rule:** the existing `telemetry_events` `bot_request` event stores `audit_id` only; the audit row is canonical (no duplicate payload storage).

**No PII** in payloads (re-affirms DEC-009). Audit rows are append-only.

**To finalise (Phase J):** retention window, archival path, exact field types — see [docs/security/audit-policy.md](security/audit-policy.md) (planned) and the new `bot_audit` section of [plan/architecture.md](../plan/architecture.md) (planned).

---

## DEC-012 — Responsible AI guardrail pipeline (multi-layered)

**Date:** 2026-04-28
**Status:** Proposed (placeholder — to be finalised by Phase I5)

The bot enforces astronomy-only, safe responses through a **multi-layered** guardrail pipeline rather than relying on any single check:

1. **Input validator** — schema + size limits
2. **Topic classifier (embedding gate)** — cosine similarity vs. NASA-corpus centroid; reject if below threshold τ
3. **Prompt-injection heuristics** — regex set + provenance checks for "ignore previous instructions"-style attacks
4. **Multi-agent pipeline** — system-prompt hard rules in every agent
5. **Output validator** — re-checks the response is on-topic and free of secret-leak patterns
6. **Audit write** — every verdict persisted to `bot_audit` (DEC-013)

**Why multi-layered:** no single technique is robust; the embedding gate is cheap and deterministic, prompt-injection heuristics catch a different failure mode, and the output validator catches drift. Single-layer was rejected.

**Abuse / overuse controls** layered on top: per-session call cap, per-user daily quota, token budget per session, repeated-question detector. Each control has an explicit threshold, counter location (in `bot_audit`), and refusal message.

**To finalise (Phase I):** threshold τ, regex set, control thresholds, refusal text — see [docs/security/rai-policy.md](security/rai-policy.md) (planned) and `docs/paper/figures/rai-pipeline.md` (planned).

---

## DEC-011 — Security architecture & STRIDE threat model

**Date:** 2026-04-28
**Status:** Proposed (placeholder — to be finalised by Phase H5)

We adopt **STRIDE** (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) as the threat-modeling vocabulary for the MAIVE backend. Trust boundaries are explicit: **Client ↔ FastAPI**, **FastAPI ↔ Cosmos DB**, **FastAPI ↔ LLM provider** (Ollama or Azure AI Foundry).

**Why STRIDE:** industry-standard, easy to audit by external reviewers (PhD committee), and pairs cleanly with the V-Model right-arm verification gates (Phase K).

**Each threat must carry a verdict:** (a) implemented (cite file), (b) planned (cite plan ID), or (c) accepted-risk (cite DEC-NNN). No threat without a verdict.

**To finalise (Phase H):** populated STRIDE table, trust-boundary diagram, secrets inventory, mitigation matrix — see [docs/security/threat-model.md](security/threat-model.md) (planned), [docs/security/secrets-inventory.md](security/secrets-inventory.md) (planned), and `docs/paper/figures/trust-boundaries.md` (planned).

---

## DEC-010 — Living documentation discipline

**Date:** 2026-04-28
**Status:** Accepted

We adopt a four-file documentation system to keep the project coherent across long-running PhD work and across AI-agent sessions:

| File | Role |
|---|---|
| [AGENTS.md](../AGENTS.md) | Always-loaded project brief — identity rule, unified bot rule, Clean Architecture rule, rules of engagement |
| [docs/plan.md](plan.md) | Public mirror of the working plan; phases, sequencing, verification gates |
| [docs/status.md](status.md) | Running status board: current sprint, blockers, weekly changelog. Read first in any new session |
| [docs/decisions.md](decisions.md) | This file — reverse-chronological architectural decisions |

In addition, an **extended systems-engineering paper** ([docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md)) acts as the long-form internal record of the architecture, with a publishable derivative produced after data collection completes.

**Enforcement:** Every architectural change must (a) append a `DEC-NNN` entry here, (b) update `docs/status.md` weekly, and (c) cross-reference the relevant section in the extended paper. Backend file instructions in `.github/instructions/` and the `maive-lead` agent enforce this.

---

## DEC-009 — Unified `(platform, platform_user_id)` identity model

**Date:** 2026-04-28
**Status:** Accepted

All clients (web, Unity, Spatial.io, VRChat) share the same backend API. Each client identifies its user with a `(platform, platform_user_id)` natural key on first contact via a new endpoint:

```
POST /api/users/identify
{ "platform": "web" | "unity" | "spatial.io" | "vrchat" | "sinespace",
  "platform_user_id": "<provider-issued ID>",
  "display_name": "<optional>" }
```

The endpoint is **idempotent** — repeated calls with the same `(platform, platform_user_id)` return the same internal `user.id` (UUID). No PII (no email, no real name).

**Why:**
- Unity, Spatial.io, VRChat, and the flat web client cannot share a single auth scheme; the natural-key approach decouples identity from any specific platform's auth.
- Aligns with the multi-platform research design — same telemetry pipeline regardless of how the participant accesses MAIVE.
- The `User` entity drops the legacy `spatial_id` field and the redundant `group` field (experimental condition is already on `Session.condition`).

**Pre-deployment hardening (out of scope for the thesis):** add a `X-Maive-Platform-Token` header check before any public release.

---

## DEC-008 — Spatial.io API integration is research-blocked

**Date:** 2026-04-28
**Status:** Accepted

Spatial.io currently does not expose a server-side API that allows a Spatial scene to call our FastAPI backend directly. We do **not** abandon Spatial.io, but we mark it as research-blocked and document the workaround:

**Workaround:** Embed a minimal web view inside the Spatial.io scene that loads the standard MAIVE flat-web client at `/learn`. The web view sends `platform = "spatial.io"` so all telemetry and bot interactions flow through the unified backend with the correct provenance.

**Tracking:**
- Notes and experiments live in `src/unity/sandbox_26/spatial_research/NOTES.md`
- We re-evaluate quarterly whether Spatial.io has shipped server-callable APIs
- The thesis can still report Spatial.io as a deployment target via the web-view bridge

---

## DEC-007 — Platform identifiers standardised

**Date:** 2026-04-15
**Status:** Accepted

The `platform` field on `Session` now uses the official product names:

| Value | Platform | Description |
|-------|----------|-------------|
| `spatial.io` | Spatial.io | Primary VR platform for immersive collaboration |
| `vrchat` | VRChat | Community-driven VR social platform |
| `sinespace` | Sine Space | Cross-platform virtual world |
| `web` | Web (flat) | Browser-based 2D fallback for accessibility |

Previous values (`spatial`, `sines`) are deprecated.

---

## DEC-006 — Unified bot endpoint (`/api/bot/ask`)

**Date:** 2026-04-06
**Status:** Accepted

Unity sends one identical request for both experimental conditions. The backend inspects `session.condition` to route:

- `non-adaptive-vr` → static help-content DB lookup (control group)
- `maive` → full multi-agent AI pipeline

This keeps the Unity client condition-agnostic and simplifies data collection.

---

## DEC-005 — Multi-agent architecture (4 agents)

**Date:** 2026-04-06
**Status:** Accepted

The adaptive AI system uses four specialised agents orchestrated by the Coordination Agent:

| Agent | Responsibility |
|-------|---------------|
| **User Modeling** | Reads telemetry, computes engagement metrics, identifies knowledge gaps |
| **Content Curation** | Queries RAG vector store for NASA content, crafts help responses |
| **Assessment** | Evaluates Zone of Proximal Development fit, recommends difficulty adjustment |
| **Coordination** | Orchestrates the other three, picks the single highest-priority action, persists `AgentAction` |

Control-group sessions (`condition = "non-adaptive-vr"`) always receive `no_action`.

---

## DEC-004 — LLM provider abstraction layer

**Date:** 2026-04-06
**Status:** Accepted

An abstract `LLMProvider` interface decouples all agent code from any specific LLM SDK:

- **Local dev:** `OllamaProvider` (httpx → Ollama REST API, default models `llama3` + `nomic-embed-text`)
- **Production:** `AzureFoundryProvider` (openai SDK → Azure AI Foundry)

Switched via `LLM_PROVIDER` env var (`ollama` | `azure`). Agents never import a provider directly.

---

## DEC-003 — RAG with Cosmos DB vector search

**Date:** 2026-04-06
**Status:** Accepted

NASA educational content is chunked, embedded, and stored in a `knowledge_documents` Cosmos DB container with DiskANN vector indexing. The Content Curation Agent queries it at runtime.

Ingestion pipeline: markdown → section parsing → word-based chunking (512 words, 64 overlap) → batch embedding → Cosmos DB.

---

## DEC-002 — Static bot content for control group

**Date:** 2026-04-06
**Status:** Accepted

The `non-adaptive-vr` condition uses a `help_content` Cosmos DB container with pre-authored help entries keyed by `planet` (partition key), `section`, `content_topic`, `difficulty_level`, and `help_type`. No LLM calls involved.

---

## DEC-001 — Clean Architecture + Cosmos DB

**Date:** 2026-03-28
**Status:** Accepted

Backend follows Clean Architecture:

```
API (FastAPI routes) → Application (DTOs, Use Cases) → Domain (Entities, Interfaces) → Infrastructure (Cosmos DB, AI)
```

All repositories implement domain interface ports. Cosmos DB chosen for elastic scale, low latency, multi-region writes, and built-in vector search.

Base repository class (`BaseCosmosRepository`) provides shared init, Cosmos metadata stripping, and datetime serialisation to eliminate boilerplate across 11 containers.
