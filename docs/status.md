# MAIVE — Project Status

> **Running status board.** Updated whenever meaningful work merges. Read this *first* in any new session.
> Last updated: **2026-04-28**

## Current sprint focus

**Sprint goal:** Establish the persistent agent + documentation system so any future session immediately understands the project state. Then unblock multi-platform integration via the unified `(platform, platform_user_id)` identity model.

**Active phases:** A (agent customization) · F1–F4 (documentation) · *next:* B (identity model)

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
| A2 | maive-lead.agent.md | 🟡 In progress |
| A3 | backend Clean Architecture instructions | 🟡 In progress |
| A4 | frontend React instructions | 🟡 In progress |
| B1–B4 | Identity model (Student `(platform, platform_user_id)`) | ⬜ Not started |
| C1 | Flat web `/learn` reference client | ⬜ Not started |
| C2 | Unity SDK adapter spec | ⬜ Not started |
| C3 | Spatial.io research notes (research-blocked) | ⬜ Not started |
| C4 | VRChat integration notes | ⬜ Not started |
| D1 | `seed_help_content.py` CLI | ⬜ Not started |
| D2 | NASA ingestion docs | ⬜ Not started |
| D3 | Demo seeder (optional) | ⬜ Not started |
| E1 | `.env.example` updates | ⬜ Not started |
| E2 | `GET /api/health/llm` | ⬜ Not started |
| E3 | `GET /api/health` extended | ⬜ Not started |
| F1 | docs/plan.md | ✅ Done (2026-04-28) |
| F2 | docs/status.md (this file) | ✅ Done (2026-04-28) |
| F3 | docs/decisions.md DEC-008/009/010 | 🟡 In progress |
| F4 | docs/paper extended SE paper | 🟡 In progress |
| F5 | docs/paper publishable derivative | ⬜ Deferred (Aug 2026) |
| F6 | docs/paper/figures (Mermaid) | ⬜ Not started |
| F7 | docs/paper/README.md (workflow guide) | ⬜ Not started |
| F8 | Source-file cross-link discipline | ⬜ Ongoing |

**Legend:** ⬜ Not started · 🟡 In progress · ✅ Done · 🚫 Blocked · ⏸ Deferred

---

## What changed this week

### 2026-04-28
- **Phase A1 complete** — `AGENTS.md` created at workspace root with project brief, identity rule, unified bot rule, LLM provider rule, and rules of engagement
- **Phase F1 complete** — `docs/plan.md` now mirrors the working session plan publicly
- **Phase F2 complete** — this status file created
- **Phase F3 in progress** — DEC-008 (Spatial.io API limitation), DEC-009 (unified identity model), DEC-010 (documentation discipline) being added to `docs/decisions.md`
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
