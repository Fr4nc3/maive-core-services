# MAIVE Core Services — Project Plan

> **Public mirror** of the working session plan. Source of truth for committee, advisors, and contributors.
> Last updated: 2026-04-28

## TL;DR

Establish a **persistent agent + always-loaded instructions** so any future Copilot/Claude session knows the thesis context, architecture, and conventions. Establish a **living documentation system** — plan tracker, status file, decision-log discipline, and a **systems-engineering paper** (extended internal version + publishable derivative). Then extend the existing backend so that **all clients** (flat web, Unity single-player, Spatial.io, VRChat) hit the **same unified API** with a per-user `(student_id, platform)` identity. Wire the LLM provider (Azure ↔ Ollama) cleanly via env config, and ship two seed scripts (NASA RAG + static help content) so the system is reproducible end-to-end.

The infrastructure for the unified bot, multi-agent pipeline, RAG, and LLM abstraction is **already built**.

---

## Phase A — Persistent Project Memory

| ID | Artifact | Status |
|---|---|---|
| **A1** | [AGENTS.md](../AGENTS.md) — workspace-root, always-loaded brief | ✅ Done |
| **A2** | `.github/agents/maive-lead.agent.md` — invokable PhD-aware lead agent | 🟡 In progress |
| **A3** | `.github/instructions/backend-clean-architecture.instructions.md` — `applyTo: src/backend/app/**/*.py` | 🟡 In progress |
| **A4** | `.github/instructions/frontend-react.instructions.md` — `applyTo: src/frontend/src/**/*.{ts,tsx}` | 🟡 In progress |

## Phase B — Identity & Platform Model

| ID | Change | Status |
|---|---|---|
| **B1** | Extend `Student`: `platform_user_id` + `platform` + `display_name` (drop `spatial_id`, drop `group`) | ⬜ Not started |
| **B2** | New `IdentifyOrCreateStudentUseCase` | ⬜ Not started |
| **B3** | New `POST /api/students/identify` endpoint (idempotent) | ⬜ Not started |
| **B4** | Repo method `get_by_platform_identity(platform, platform_user_id)` | ⬜ Not started |

## Phase C — Multi-Client Integration Patterns

| ID | Client | Notes | Status |
|---|---|---|---|
| **C1** | Flat web `/learn` page | **Reference implementation** — fastest iteration | ⬜ Not started |
| **C2** | Unity single-player | Spec for `MaiveClient.cs` adapter (no code yet) | ⬜ Not started |
| **C3** | Spatial.io | Research-blocked (DEC-008); fallback via embedded web view | ⬜ Not started |
| **C4** | VRChat | UDON GET-only via `VRCStringDownloader`; POST via web-view bridge | ⬜ Not started |

## Phase D — Seed Scripts & Reproducibility

| ID | Script | Status |
|---|---|---|
| **D1** | `app/cli/seed_help_content.py` — load `data/help_content/<planet>/*.json` | ⬜ Not started |
| **D2** | NASA ingestion docs (script already exists) — `data/nasa/<body>.md` layout | ⬜ Not started |
| **D3** | `app/cli/seed_demo.py` — one demo student + session per platform (optional) | ⬜ Not started |

## Phase E — LLM Provider Wiring (verify, don't rebuild)

| ID | Action | Status |
|---|---|---|
| **E1** | `.env.example` documents both Ollama and Azure modes | ⬜ Not started |
| **E2** | `GET /api/health/llm` — pings provider, returns `{provider, model, ok, latency_ms}` | ⬜ Not started |
| **E3** | Extend `/api/health` with `cosmos_ok`, `llm_ok` | ⬜ Not started |

## Phase F — Living Documentation & Systems-Engineering Paper

| ID | Artifact | Status |
|---|---|---|
| **F1** | [docs/plan.md](plan.md) — this file | ✅ Done |
| **F2** | [docs/status.md](status.md) — running status board | 🟡 In progress |
| **F3** | [docs/decisions.md](decisions.md) discipline (DEC-008..010 added) | 🟡 In progress |
| **F4** | [docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md) — internal extended paper | ⬜ Not started |
| **F5** | [docs/paper/maive-systems-engineering-publishable.md](paper/maive-systems-engineering-publishable.md) — publishable derivative | ⬜ Deferred to Aug 2026 (post-data collection) |
| **F6** | `docs/paper/figures/` — Mermaid sources | ⬜ Not started |
| **F7** | [docs/paper/README.md](paper/README.md) — paper-development guide | ⬜ Not started |
| **F8** | Cross-link discipline in source files | ⬜ Ongoing |

---

## Sequencing

1. A1 (AGENTS.md) ✅
2. F1 + F2 + F3 (plan, status, decision discipline) — *parallel with A1*
3. A2 (lead agent) — *depends on A1 + F2*
4. A3 + A4 (file instructions) — *parallel with A2*
5. F4 (extended paper scaffold) — *after A1 + F1–F3*
6. F7 (paper guide) — *after F4*
7. B1–B4 (identity model) — *parallel with A/F*
8. E1–E3 (LLM env + health) — *parallel with B*
9. D1 (help content seeder) — *after backend stable*
10. D2 (NASA ingestion docs) — *parallel with D1*
11. C1 (flat web learner view) — *depends on B3*
12. C2/C3/C4 (Unity, Spatial, VRChat docs) — *parallel after C1*
13. F6 (figures) — *after C1–C4*
14. D3 (demo seeder) — *last for build*, optional
15. F5 (publishable paper) — *post-data collection (Aug 2026)*

---

## Verification gates

1. **Agent customization smoke test** — open a fresh chat; agent reads AGENTS.md + status.md and summarises current focus
2. **Backend lint** — `cd src/backend && uv run ruff check .` exits 0
3. **Identity flow** — `POST /api/students/identify` is idempotent
4. **Health checks** — `GET /api/health` and `GET /api/health/llm` return 200
5. **Help content seeder** — `data/help_content/mars/*.json` → `GET /api/help?planet=mars` returns it
6. **NASA ingestion** — `data/nasa/sun.md` → `POST /api/bot/ask` returns NASA-sourced content
7. **Unified bot parity** — same payload from web client and Unity client produces equivalent responses
8. **Decision log freshness** — DEC-008, DEC-009, DEC-010 logged
9. **Status file freshness** — last-updated within 7 days of any merged change
10. **Plan parity** — this file's headings match `/memories/session/plan.md`
11. **Extended paper coverage** — every shipped phase has a paragraph in F4

---

## Open considerations

1. **AGENTS.md location** — workspace root chosen (auto-discovered by Claude + Copilot, visible to PhD committee)
2. **Identify endpoint auth** — no auth pre-defence; add `X-Maive-Platform-Token` header check before any public deployment
3. **Unity C# scaffolding now or after web client?** — defer; build web reference client first to lock the API contract
