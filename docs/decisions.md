# MAIVE — Decision Log

All architectural and design decisions for the MAIVE platform, in reverse chronological order.

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
