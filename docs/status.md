# MAIVE — Project Status

> **Running status board.** Updated whenever meaningful work merges. Read this *first* in any new session.
> Last updated: **2026-04-29**

## Current sprint focus

**Sprint goal:** Phase R (RAI Bot Pipeline) shipped 2026-04-29 — `/api/bot/ask`
now traverses 6 guardrail stages with an immutable `bot_audit` row. Granular
sub-agent surface (Phase W) live. Sample help_content seeded for the
non-adaptive control arm. Next: Phase X (rate limiting + Content Safety
integration) and execute the operator-side V steps (`docker compose up`,
`azd provision --preview`).

**Active phases:** ⏳ G (V-Model + traceability) · ⏳ H (STRIDE threat model — base done; expand per-feature) · ⏳ I (RAI policy — base done; expand) · ⏳ J (audit & evidence — base done) · ⏳ K (V&V test catalog) · ⏳ L (cross-link discipline) · ⏳ N (bilingual EN/ES) · ⏳ X (per-session rate limit + Content Safety)

## What changed this week
- **2026-04-29** — System review snapshot authored: [`docs/system-review-2026-04-29.md`](system-review-2026-04-29.md) (services, plan, infra, status, API surface, telemetry → RQ traceability, gap audit, fitness-to-research scorecard).
- **2026-04-29** — Phase R shipped: 6-stage RAI bot pipeline (`input_validator → topic_gate → prompt_injection → system_prompt → CoordinationAgent → output_validator → audit`), `BotAudit` entity + Cosmos repo + explicit `bot_audit` container in Bicep, `BotPipelineUseCase` orchestrator, both AI and static `/api/bot/ask` paths now write audit rows. 42/42 RAI tests passing. DEC-019 + DEC-020 added. [`docs/rai-policy.md`](rai-policy.md) and [`docs/threat-model.md`](threat-model.md) authored. `qa_audit rai-check` upgraded to verify modules + container + wiring (15+ checks). Phase W shipped: `@maive-deploy`, `@maive-frontend`, `@maive-research` sub-agents + `deploy.instructions.md` + top-level dispatcher [`.github/copilot-instructions.md`](../.github/copilot-instructions.md). Phase P4 shipped: narrowed `except Exception` in `health.py` (httpx/OpenAIError/CosmosHttpResponseError) and 3 cosmos repos (CosmosResourceNotFoundError); audit-write blocks remain broad by design (DEC-019). Phase S sample seeded: `data/help_content/mars/atmosphere.json` (3 EN + 3 ES across `fact`/`hint`/`explanation`).
- **2026-04-28** — Phase Q shipped: [`RUNLOCAL.md`](RUNLOCAL.md) (Path A `.venv` + Path B Docker Compose), backend + frontend Dockerfiles + nginx template, `docker-compose.yml`, Edge Protector ([`src/edge-protector/`](../src/edge-protector/)), full `infra/` Bicep (App Service B1 frontend + Container Apps backend + Cosmos serverless + AI Foundry + Key Vault + ACR + Log Analytics + App Insights), `azure.yaml`, CI + deploy workflows, [`docs/deployment/`](deployment/) trio (architecture / runbook / secrets). DEC-017 + DEC-018 added.
- **2026-04-28** — Phase P1 shipped: `LLMProviderRegistry` removes the if/elif provider switch in `dependencies.py` + `health.py`; `LLMProvider.model_name` added; both providers self-register via decorator. DEC-016 added. P2/P3 explicitly deferred (no if/elif present to remove). Also fixed 2 `datetime.utcnow()` violations.
- **2026-04-28** — Phase O shipped: `@maive-qa` agent + `qa_audit.py` (5 rubrics) + checklist. DEC-015 added. Surfaced concrete Phase P targets: 4 if/elif provider sites in `dependencies.py` + `health.py`, 2 `datetime.utcnow()` calls, 5 bare `except Exception` blocks.

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
| F4 | docs/paper extended SE paper | 🟡 Skeleton landed; superseded section-by-section by Phases G/I/J/K |
| F5 | docs/paper publishable derivative | ⏸ Deferred (Aug 2026) |
| F6 | docs/paper/figures (Mermaid) | 🟡 In progress (Phase G) |
| F7 | docs/paper/README.md (workflow guide) | ✅ Done (2026-04-28) |
| F8 | Source-file cross-link discipline | 🟡 In progress (Phase L) |
| **G1–G5** | V-Model + traceability + components + DFD + deployment figures | ⬜ Not started |
| **H1–H5** | STRIDE threat model, trust boundaries, secrets inventory, mitigations, DEC-011 | ⬜ Not started (DEC-011 placeholder seeded) |
| **I1–I5** | Responsible AI policy, pipeline figure, centroid spec, abuse controls, DEC-012 | ⬜ Not started (DEC-012 placeholder seeded) |
| **J1–J4** | `bot_audit` container schema, audit policy, telemetry linkage, DEC-013 | ⬜ Not started (DEC-013 placeholder seeded) |
| **K1–K5** | V&V test catalog (security + RAI), V-Model right-arm trace, paper §3 update | ⬜ Not started |
| **L1–L4** | Cross-link headers in source files; status/plan reconciliation | 🟡 L3+L4 done; L1+L2 not started |
| **N1–N3** | Bilingual data model: `Student.preferred_language`, `Session.language`, `BotAskRequest.language` + resolution | ⬜ Not started |
| **N4–N6** | Agent prompts EN/ES split, static help language field, RAG language tagging + fallback | ⬜ Not started |
| **N7–N8** | Frontend i18n (selector, `en.json`/`es.json`, `<html lang>`); researcher `language` column | ⬜ Not started |
| **N9–N10** | Telemetry/audit `language` field; backfill defaults | ⬜ Not started |
| **N11–N12** | DEC-014 + paper §11 update + `figures/language-flow.md` | 🟡 DEC-014 placeholder seeded |

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
- **Phases G–L planned** — V-Model + secure-system validation pack (doc-only) recorded in `docs/plan.md`; DEC-011/012/013 placeholders seeded in `docs/decisions.md`; status table extended with G–L rows; A–F rows reconciled
- **Phase N planned** — Bilingual (English / Spanish) end-to-end recorded in `docs/plan.md`: `preferred_language` on Student, `language` on Session, `language` on `BotAskRequest`, resolution order `request → session → student → "en"`, EN/ES split for agent prompts, static help, and NASA RAG, frontend i18n, telemetry/audit `language` field. DEC-014 placeholder seeded in `docs/decisions.md`.

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

1. **G1** — author Mermaid V-Model figure (`docs/paper/figures/vmodel.md`)
2. **G3 + G5** — component diagram + deployment topology (parallel with G1)
3. **H1 + H2** — STRIDE threat model + trust-boundary diagram (parallel track)
4. **G2** — traceability matrix (depends on G1)
5. **I1 + I2** — Responsible AI policy + pipeline figure (depends on H1–H2)
6. **J1** — `bot_audit` schema in `plan/architecture.md` (depends on I2)
7. **K1–K4** — V&V test catalog (depends on G2 + H4 + I4 + J1)
8. **L1 + L2** — source-file cross-link headers (last)
9. **N1 + N2** — bilingual data model: `Student.preferred_language` + `Session.language` (parallel track)
10. **N3** — `BotAskRequest.language` + resolution order in `bot.py`
11. **N4 + N5 + N6** — agent prompts EN/ES split, static help language field, RAG language tagging
12. **N7 + N8** — frontend language selector + i18n + dynamic `<html lang>`

---

## Links

- [docs/plan.md](plan.md) — full plan
- [docs/decisions.md](decisions.md) — architectural decisions
- [plan/architecture.md](../plan/architecture.md) — architecture spec
- [plan/telemetry-model.md](../plan/telemetry-model.md) — telemetry events
- [docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md) — extended SE paper
