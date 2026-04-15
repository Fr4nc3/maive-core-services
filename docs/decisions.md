# MAIVE — Decision Log

All architectural and design decisions for the MAIVE platform, in reverse chronological order.

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
