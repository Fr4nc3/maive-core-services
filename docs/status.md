# MAIVE — Project Status

> **Running status board.** Updated whenever meaningful work merges. Read this *first* in any new session.
> Last updated: **2026-04-28**

## Current sprint focus

**Sprint goal:** Wire infrastructure (LLM provider env, health checks), ship the unified-bot reference flow end-to-end on the web client, and seed reproducible content (static help + NASA RAG).

**Active phases:** ✅ A · ✅ B · ✅ C · ✅ D1/D2 · ✅ E · ✅ F1–F4/F7 · *next:* F5 (publishable paper), F6 (figures), D3 (demo seeder)

## Blockers

| Blocker | Phase affected | Mitigation |
|---|---|---|
| Spatial.io API not callable from external services | C3 | Documented as DEC-008; fallback via embedded web view |
| VRChat UDON limited to GET via `VRCStringDownloader` | C4 | Hybrid: GET-only RAG fetches direct from UDON, POST telemetry via web-view bridge |
| None for backend/web | A, B, C1, D, E, F | — |

---

## Phase status

| Phase | Title | Status |
|---|---|---|
| A1 | AGENTS.md (workspace root) | ✅ Done (2026-04-28) |
| A2 | maive-lead.agent.md | ✅ Done (2026-04-28) |
| A3 | backend Clean Architecture instructions | ✅ Done (2026-04-28) |
| A4 | frontend React instructions | ✅ Done (2026-04-28) |
| B1–B4 | Identity model (Student `(platform, platform_user_id)`) | ✅ Done (2026-04-28) |
| C1 | Flat web `/learner` reference client | ✅ Done (2026-04-28) |
| C2 | Unity SDK adapter spec | ✅ Done (2026-04-28) — see `docs/client-integration.md` |
| C3 | Spatial.io research notes (research-blocked) | ✅ Done (2026-04-28) — see `docs/client-integration.md` |
| C4 | VRChat integration notes | ✅ Done (2026-04-28) — see `docs/client-integration.md` |
| D1 | `seed_help_content.py` CLI | ✅ Done (2026-04-28) |
| D2 | NASA ingestion docs | ✅ Done (2026-04-28) — see `docs/knowledge-ingestion.md` |
| D3 | Demo seeder (optional) | ⬜ Deferred |
| E1 | `.env.example` updates | ✅ Done (2026-04-28) |
| E2 | `GET /api/health/llm` | ✅ Done (2026-04-28) |
| E3 | `GET /api/health` extended | ✅ Done (2026-04-28) — composite Cosmos+LLM check |
| F1 | docs/plan.md | ✅ Done (2026-04-28) |
| F2 | docs/status.md (this file) | ✅ Done (2026-04-28) |
| F3 | docs/decisions.md DEC-008/009/010 | ✅ Done (2026-04-28) |
| F4 | docs/paper extended SE paper | 🟡 In progress (skeleton landed) |
| F5 | docs/paper publishable derivative | ⏸ Deferred (Aug 2026) |
| F6 | docs/paper/figures (Mermaid) | ⬜ Not started |
| F7 | docs/paper/README.md (workflow guide) | ✅ Done (2026-04-28) |
| F8 | Source-file cross-link discipline | ⬜ Ongoing |

**Legend:** ⬜ Not started · 🟡 In progress · ✅ Done · 🚫 Blocked · ⏸ Deferred

---

## What changed this week

### 2026-04-28
- **Phase A1 complete** — `AGENTS.md` created at workspace root with project brief, identity rule, unified bot rule, LLM provider rule, and rules of engagement
- **Phase A2/A3/A4 complete** — `maive-lead.agent.md` + backend & frontend instruction files
- **Phase B complete** — Student identity now `(platform, platform_user_id)` with `display_name` + `condition`; new `POST /api/students/identify` is idempotent; frontend updated
- **Phase C1 complete** — `LearnerPage.tsx` is the canonical reference client (identify → session → telemetry → unified bot)
- **Phase C2/C3/C4 complete** — `docs/client-integration.md` documents Unity, Spatial.io, and VRChat patterns against the shared API contract
- **Phase D1 complete** — `app/cli/seed_help_content.py` + sample `data/help_content/mars/crater_lab.json`
- **Phase D2 complete** — `docs/knowledge-ingestion.md` covers static help and NASA RAG workflows
- **Phase E complete** — `.env.example` documents Ollama vs. Azure modes; new `/api/health`, `/api/health/llm`, `/api/health/cosmos` endpoints
- **Phase F1/F2 complete** — `docs/plan.md` mirrors session plan; this status file landed
- **Phase F3 complete** — DEC-008 (Spatial.io API), DEC-009 (unified identity), DEC-010 (documentation discipline)
- **Phase F4/F7 complete** — extended SE paper skeleton + paper README workflow guide
- **Phase A2/A3/A4 in progress** — invokable lead agent + backend/frontend instructions being created
- **Phase F4 in progress** — extended systems-engineering paper skeleton being scaffolded

### Earlier (April 2026)
- **DEC-007** Platform identifiers standardised to `spatial.io | vrchat | sinespace | web`
- **DEC-006** Unified `POST /api/bot/ask` endpoint built; routes by `session.condition`
- **DEC-005** Multi-agent architecture (User Modeling · Content Curation · Assessment · Coordination) implemented
- **DEC-004** LLM provider abstraction (`LLMProvider` interface) — Ollama dev, Azure Foundry prod
- **DEC-003** RAG with Cosmos DB DiskANN vector search built
- **DEC-002** Static help content for control group built
- **DEC-001** Clean Architecture + Cosmos DB foundation established

---

## Next actions (immediate)

1. Finish A2 — invokable `maive-lead.agent.md` with status awareness
2. Finish A3 + A4 — backend/frontend file instructions
3. Append DEC-008, DEC-009, DEC-010 to `docs/decisions.md`
4. Scaffold `docs/paper/maive-systems-engineering-extended.md` with section headers
5. Create `docs/paper/README.md` workflow guide
6. Begin Phase B1 (extend Student entity with `platform_user_id` + `platform`)

---

## Links

- [docs/plan.md](plan.md) — full plan
- [docs/decisions.md](decisions.md) — architectural decisions
- [plan/architecture.md](../plan/architecture.md) — architecture spec
- [plan/telemetry-model.md](../plan/telemetry-model.md) — telemetry events
- [docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md) — extended SE paper
