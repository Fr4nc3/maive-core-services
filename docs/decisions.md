# MAIVE — Decision Log

All architectural and design decisions for the MAIVE platform, in reverse chronological order.

---

## DEC-014 — Bilingual support model (English / Spanish)

**Date:** 2026-04-28
**Status:** Accepted

The MAIVE experience and service must respect a learner's preferred language (`en` or `es`) end-to-end: client UI, session record, static help content, NASA RAG retrieval, agent prompts, bot response, and telemetry/audit. Language is recorded as a research-grade variable so RQ1/RQ2/RQ3 analyses can be split by language.

**Resolution order (effective language for any bot/help call):**
1. `BotAskRequest.language` (per-request override)
2. `Session.language` (per-session override of student default)
3. `Student.preferred_language` (set on `POST /api/students/identify`)
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

**Schema (draft):** `id, session_id, student_id, timestamp, request_payload, response_payload, guardrail_verdicts[{stage, verdict, score, rule_hit}], provider, model, prompt_tokens, completion_tokens, latency_ms, condition`.

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

**Abuse / overuse controls** layered on top: per-session call cap, per-student daily quota, token budget per session, repeated-question detector. Each control has an explicit threshold, counter location (in `bot_audit`), and refusal message.

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
POST /api/students/identify
{ "platform": "web" | "unity" | "spatial.io" | "vrchat" | "sinespace",
  "platform_user_id": "<provider-issued ID>",
  "display_name": "<optional>" }
```

The endpoint is **idempotent** — repeated calls with the same `(platform, platform_user_id)` return the same internal `student.id` (UUID). No PII (no email, no real name).

**Why:**
- Unity, Spatial.io, VRChat, and the flat web client cannot share a single auth scheme; the natural-key approach decouples identity from any specific platform's auth.
- Aligns with the multi-platform research design — same telemetry pipeline regardless of how the participant accesses MAIVE.
- The `Student` entity drops the legacy `spatial_id` field and the redundant `group` field (experimental condition is already on `Session.condition`).

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
