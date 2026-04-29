# MAIVE Core Services — Project Plan

> **Public mirror** of the working session plan. Source of truth for committee, advisors, and contributors.
> Last updated: 2026-04-29
>
> **Plan template:** All phases added on or after 2026-04-29 follow
> [`plan-template.md`](plan-template.md) (Pillar / Goal / Owner agent / Status
> header + tasks table + Verification + DECs + Out-of-scope). Restructures of
> this file are logged in [`plan-history.md`](plan-history.md). Pre-template
> phases are preserved below the `--- Pre-template phases ---` divider for
> historical fidelity and will be migrated lazily.

## Phase R — RAI Bot Pipeline (DEC-019)

**Pillar:** Stable Core
**Goal:** Every `/api/bot/ask` call traverses 6 RAI guardrail stages and writes one immutable `bot_audit` row.
**Owner agent:** @maive-rai
**Status:** ✅ Done (2026-04-29)

| ID | Artifact | Status |
|---|---|---|
| **R1** | `BotAudit` entity + `BotAuditRepository` interface (append-only) | ✅ Done (2026-04-29) |
| **R2** | 6 guardrail modules + `errors.py` under `src/backend/app/infrastructure/rai/` | ✅ Done (2026-04-29) |
| **R3** | `BotPipelineUseCase` orchestrator | ✅ Done (2026-04-29) |
| **R4** | `CosmosBotAuditRepository` + DI wiring | ✅ Done (2026-04-29) |
| **R5** | `bot_audit` container in `infra/modules/cosmos.bicep` (PK `/session_id`) | ✅ Done (2026-04-29) |
| **R6** | `routes/bot.py` AI + static paths use the pipeline / write audit | ✅ Done (2026-04-29) |
| **R7** | [`docs/rai-policy.md`](rai-policy.md) + [`docs/threat-model.md`](threat-model.md) | ✅ Done (2026-04-29) |
| **R8** | `qa_audit rai-check` upgraded (modules + container + wiring) | ✅ Done (2026-04-29) |
| **R9** | `tests/rai/` — 42 tests covering each stage + integration | ✅ Done (2026-04-29) |
| **R10** | DEC-019 added to [`docs/decisions.md`](decisions.md) | ✅ Done (2026-04-29) |

**Verification:** `cd src/backend && uv run pytest tests/rai/ -q` → 42/42; `qa_audit rai-check` → 16/16.
**Decisions referenced:** DEC-012, DEC-013, DEC-019.

## Phase W — Granular sub-agent surface (DEC-020)

**Pillar:** Stable Core
**Goal:** Split monolithic agent surface into a top-level dispatcher + 4 owner sub-agents (rai/deploy/frontend/research) so each turn has a smaller blast radius.
**Owner agent:** @maive-lead
**Status:** ✅ Done (2026-04-29)

| ID | Artifact | Status |
|---|---|---|
| **W1** | Top-level dispatcher [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | ✅ Done (2026-04-29) |
| **W2** | `@maive-rai` agent + [`rai.instructions.md`](../.github/instructions/rai.instructions.md) | ✅ Done (2026-04-29) |
| **W3** | `@maive-deploy` agent + [`deploy.instructions.md`](../.github/instructions/deploy.instructions.md) | ✅ Done (2026-04-29) |
| **W4** | `@maive-frontend` agent | ✅ Done (2026-04-29) |
| **W5** | `@maive-research` agent | ✅ Done (2026-04-29) |
| **W6** | Dispatcher delegation map | ✅ Done (2026-04-29) |
| **W7** | DEC-020 added to [`docs/decisions.md`](decisions.md) | ✅ Done (2026-04-29) |

**Verification:** All 5 agent files present under `.github/agents/`; dispatcher delegation map covers all 6 sub-agents.
**Decisions referenced:** DEC-020.

## Phase S — Help_content seed sample data

**Pillar:** Scenario Pack
**Goal:** Bootstrap the non-adaptive control arm with curated EN+ES help content for the Mars sample scenario.
**Owner agent:** @maive-lead
**Status:** ✅ Done (2026-04-29) — operator step S3 pending

| ID | Artifact | Status |
|---|---|---|
| **S1** | `data/help_content/mars/atmosphere.json` (3 EN + 3 ES) | ✅ Done (2026-04-29) |
| **S2** | `data/help_content/README.md` | ✅ Done (2026-04-29) |
| **S3** | Run `seed_help_content` against live Cosmos | ⏸ Operator step |

**Verification:** Pydantic validation of sample JSON returns `OK: 6 records validated`.

## Phase P4 — Narrow exception handling

**Pillar:** Stable Core
**Goal:** Replace `except Exception` with typed exceptions everywhere except the audit-write blocks sanctioned by DEC-019.
**Owner agent:** @maive-qa
**Status:** ✅ Done (2026-04-29)

| ID | Artifact | Status |
|---|---|---|
| **P4** | `health.py` + 3 cosmos repos use specific exceptions; audit-write broad-catch sanctioned by DEC-019 | ✅ Done (2026-04-29) |

**Verification:** `qa_audit if-else-scan` reports 0 bare `except Exception` outside the two sanctioned files.

## Phase V — Verification

**Pillar:** Stable Core
**Goal:** Confirm Phases O / P1 / Q / R are green via lint, RAI tests, qa_audit, and Bicep compile.
**Owner agent:** @maive-qa
**Status:** ✅ Done (2026-04-29) — operator steps V5/V6 pending

| ID | Artifact | Status |
|---|---|---|
| **V1** | Bicep compile passes | ✅ Done (2026-04-29) |
| **V2** | RAI test suite green (42/42) | ✅ Done (2026-04-29) |
| **V3** | `qa_audit all` green except pre-existing UP042 in domain entity | ✅ Done (2026-04-29) |
| **V4** | [`docs/deployment/verification-2026-04-29.md`](deployment/verification-2026-04-29.md) | ✅ Done (2026-04-29) |
| **V5** | `docker compose up` smoke | ⏸ Operator step |
| **V6** | `azd provision --preview` | ⏸ Operator step |

**Verification:** [`docs/deployment/verification-2026-04-29.md`](deployment/verification-2026-04-29.md) records the gate.

---

## Pre-template phases

> Phases below this divider were authored before [`plan-template.md`](plan-template.md)
> existed. They are kept verbatim for historical fidelity. New work or status
> changes inside these phases get a row in [`plan-history.md`](plan-history.md).

## Phase Q — Run-locally + Container deployment

**Pillar:** Stable Core
**Goal:** Stand up local-run + Azure container deployment topology (App Service frontend + Container Apps backend).
**Owner agent:** @maive-deploy
**Status:** ✅ Done (2026-04-28) — Key Vault portion superseded by Phase KV (DEC-021)

| ID | Artifact | Status |
|---|---|---|
| **Q1** | [`docs/RUNLOCAL.md`](RUNLOCAL.md) — Path A (`.venv`) + Path B (Docker Compose) | ✅ Done (2026-04-28) |
| **Q2** | [`src/backend/Dockerfile`](../src/backend/Dockerfile) + [`.dockerignore`](../src/backend/.dockerignore) (multi-stage, non-root, healthcheck) | ✅ Done (2026-04-28) |
| **Q3** | [`src/frontend/Dockerfile`](../src/frontend/Dockerfile) + [`nginx.conf.template`](../src/frontend/nginx.conf.template) + [`.dockerignore`](../src/frontend/.dockerignore) | ✅ Done (2026-04-28) |
| **Q4** | [`docker-compose.yml`](../docker-compose.yml) (backend + frontend + Cosmos emulator) | ✅ Done (2026-04-28) |
| **Q5** | [`src/edge-protector/`](../src/edge-protector/) (token + IP-allowlisted Ollama shim) | ✅ Done (2026-04-28) |
| **Q6** | [`azure.yaml`](../azure.yaml) + [`infra/main.bicep`](../infra/main.bicep) + [`infra/modules/*.bicep`](../infra/modules/) (monitoring, keyvault, cosmos, ai_foundry, containerapp, appservice) | ✅ Done (2026-04-28) |
| **Q7** | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) + [`deploy.yml`](../.github/workflows/deploy.yml) | ✅ Done (2026-04-28) |
| **Q8** | DEC-017 (LLM split) + DEC-018 (topology) | ✅ Done (2026-04-28) |
| **Q9** | [`docs/deployment/architecture.md`](deployment/architecture.md) + [`runbook.md`](deployment/runbook.md) + [`secrets.md`](deployment/secrets.md) | ✅ Done (2026-04-28) |

**Verification:** `docker compose up` boots the full local stack. `azd up`
provisions+deploys to a sandbox subscription (manual; not automated until
post-defence). CI runs lint + typecheck + build on every PR.

**Out of scope (intentionally):** VS Code Dev Containers, prod subscription
automation, Front Door / WAF, Entra ID auth, multi-region. Tracked in
[deployment/architecture.md](deployment/architecture.md) § "What is NOT here yet".

---

## Phase P — Factory / Registry refactor

| ID | Artifact | Status |
|---|---|---|
| **P1** | [`LLMProviderRegistry`](../src/backend/app/infrastructure/ai/registry.py) closes the if/elif provider switch in `dependencies.py` + `health.py`; `LLMProvider.model_name` added | ✅ Done (2026-04-28) |
| **P2** | `AgentRegistry` | 🚫 Deferred — no if/elif present (single `CoordinationAgent` entry); revisit when adding a 5th agent |
| **P3** | `CosmosRepoRegistry` | 🚫 Deferred — `_get_repo(cls)` already a class-keyed registry with no branching |
| **P5** | DEC-016 | ✅ Done (2026-04-28) |

**Verification:** `qa_audit if-else-scan` reports 0 provider hits + 0
`datetime.utcnow` hits. Remaining `except Exception` (3 cosmos repos + 3
health-route handlers) carry `# noqa: BLE001` and are intentional surface
broad-error catchers — narrow per-call when each repo gains typed exceptions.

---

## Phase O — MAIVE QA Agent (read-only audit + safe auto-fix)

| ID | Artifact | Status |
|---|---|---|
| **O1** | [`.github/agents/maive-qa.agent.md`](../.github/agents/maive-qa.agent.md) | ✅ Done (2026-04-28) |
| **O2** | [`.github/instructions/maive-qa.instructions.md`](../.github/instructions/maive-qa.instructions.md) | ✅ Done (2026-04-28) |
| **O3** | [`docs/qa/qa-checklist.md`](qa/qa-checklist.md) — 5-rubric checklist | ✅ Done (2026-04-28) |
| **O4** | [`src/backend/app/cli/qa_audit.py`](../src/backend/app/cli/qa_audit.py) | ✅ Done (2026-04-28) |
| **O5** | `qa_audit.py --fix` (ruff/prettier auto-fixers) | ✅ Done (2026-04-28) |
| **O6** | DEC-015 + VS Code task wiring | 🟡 DEC-015 done; tasks deferred |

**Run it:** `cd src/backend && uv run python -m app.cli.qa_audit all`.

**Phase P preview** (next): close the if/elif provider switches surfaced by
`qa_audit if-else-scan` via `LLMProviderRegistry`, `AgentRegistry`, and
`CosmosRepoRegistry`. See DEC-016 (planned).

---


## TL;DR

Establish a **persistent agent + always-loaded instructions** so any future Copilot/Claude session knows the thesis context, architecture, and conventions. Establish a **living documentation system** — plan tracker, status file, decision-log discipline, and a **systems-engineering paper** (extended internal version + publishable derivative). Then extend the existing backend so that **all clients** (flat web, Unity single-player, Spatial.io, VRChat) hit the **same unified API** with a per-user `(user_id, platform)` identity. Wire the LLM provider (Azure ↔ Ollama) cleanly via env config, and ship two seed scripts (NASA RAG + static help content) so the system is reproducible end-to-end.

The infrastructure for the unified bot, multi-agent pipeline, RAG, and LLM abstraction is **already built**.

---

## Phase A — Persistent Project Memory

| ID | Artifact | Status |
|---|---|---|
| **A1** | [AGENTS.md](../AGENTS.md) — workspace-root, always-loaded brief | ✅ Done (2026-04-28) |
| **A2** | `.github/agents/maive-lead.agent.md` — invokable PhD-aware lead agent | ✅ Done (2026-04-28) |
| **A3** | `.github/instructions/backend-clean-architecture.instructions.md` — `applyTo: src/backend/app/**/*.py` | ✅ Done (2026-04-28) |
| **A4** | `.github/instructions/frontend-react.instructions.md` — `applyTo: src/frontend/src/**/*.{ts,tsx}` | ✅ Done (2026-04-28) |

## Phase B — Identity & Platform Model

| ID | Change | Status |
|---|---|---|
| **B1** | Extend `User`: `platform_user_id` + `platform` + `display_name` (drop `spatial_id`, drop `group`) | ✅ Done (2026-04-28) |
| **B2** | New `IdentifyOrCreateUserUseCase` | ✅ Done (2026-04-28) |
| **B3** | New `POST /api/users/identify` endpoint (idempotent) | ✅ Done (2026-04-28) |
| **B4** | Repo method `get_by_platform_identity(platform, platform_user_id)` | ✅ Done (2026-04-28) |

## Phase C — Multi-Client Integration Patterns

| ID | Client | Notes | Status |
|---|---|---|---|
| **C1** | Flat web `/learner` page | **Reference implementation** — fastest iteration | ✅ Done (2026-04-28) |
| **C2** | Unity single-player | Spec for `MaiveClient.cs` adapter (no code yet) | ✅ Done (2026-04-28) — see [client-integration.md](client-integration.md) |
| **C3** | Spatial.io | Research-blocked (DEC-008); fallback via embedded web view | ✅ Done (2026-04-28) — see [client-integration.md](client-integration.md) |
| **C4** | VRChat | UDON GET-only via `VRCStringDownloader`; POST via web-view bridge | ✅ Done (2026-04-28) — see [client-integration.md](client-integration.md) |

## Phase D — Seed Scripts & Reproducibility

| ID | Script | Status |
|---|---|---|
| **D1** | `app/cli/seed_help_content.py` — load `data/help_content/<planet>/*.json` | ✅ Done (2026-04-28) |
| **D2** | NASA ingestion docs (script already exists) — `data/nasa/<body>.md` layout | ✅ Done (2026-04-28) — see [knowledge-ingestion.md](knowledge-ingestion.md) |
| **D3** | `app/cli/seed_demo.py` — one demo user + session per platform (optional) | ⏸ Deferred |

## Phase E — LLM Provider Wiring (verify, don't rebuild)

| ID | Action | Status |
|---|---|---|
| **E1** | `.env.example` documents both Ollama and Azure modes | ✅ Done (2026-04-28) |
| **E2** | `GET /api/health/llm` — pings provider, returns `{provider, model, ok, latency_ms}` | ✅ Done (2026-04-28) |
| **E3** | Extend `/api/health` with `cosmos_ok`, `llm_ok` | ✅ Done (2026-04-28) — composite Cosmos+LLM check |

## Phase F — Living Documentation & Systems-Engineering Paper

| ID | Artifact | Status |
|---|---|---|
| **F1** | [docs/plan.md](plan.md) — this file | ✅ Done (2026-04-28) |
| **F2** | [docs/status.md](status.md) — running status board | ✅ Done (2026-04-28) |
| **F3** | [docs/decisions.md](decisions.md) discipline (DEC-008..010 added) | ✅ Done (2026-04-28) |
| **F4** | [docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md) — internal extended paper | 🟡 Skeleton landed; superseded section-by-section by Phases G/I/J/K |
| **F5** | [docs/paper/maive-systems-engineering-publishable.md](paper/maive-systems-engineering-publishable.md) — publishable derivative | ⏸ Deferred to Aug 2026 (post-data collection) |
| **F6** | `docs/paper/figures/` — Mermaid sources | 🟡 In progress (Phase G) |
| **F7** | [docs/paper/README.md](paper/README.md) — paper-development guide | ✅ Done (2026-04-28) |
| **F8** | Cross-link discipline in source files | 🟡 In progress (Phase L) |

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
3. **Identity flow** — `POST /api/users/identify` is idempotent
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

---

## Phases G–L — V-Model + Secure-System Validation (added 2026-04-28)

> **Doc-only plan.** Builds the complete systems-engineering documentation pack (V-Model, traceability matrix, threat model, RAI policy, audit spec, V&V test catalog). No runtime code change here — implementation lands in a follow-up *Phase M — RAI/Security implementation* plan.

### Phase G — V-Model rendering & traceability

| ID | Artifact | Status |
|---|---|---|
| **G1** | `docs/paper/figures/vmodel.md` — Mermaid V-Model (left arm: Stakeholder needs → System reqs → Architecture → Module design → Implementation; right arm: Unit → Integration → System verif → Acceptance/validation; horizontal traceability arrows) | ⬜ Not started |
| **G2** | `docs/paper/traceability-matrix.md` — `RQ × CR × Verification gate` table; columns: Hypothesis · Instrument · Statistical rule · Implementing files · Test case ID · Status | ⬜ Not started |
| **G3** | `docs/paper/figures/components.md` — Mermaid component / subsystem diagram (Presentation → API → Application → Domain → Infrastructure → AI → Analytics) | ⬜ Not started |
| **G4** | `docs/paper/figures/dfd-bot-flow.md` — Mermaid DFD for canonical user journey (identify → session → telemetry → bot ask → audit → adaptive action) | ⬜ Not started |
| **G5** | `docs/paper/figures/deployment.md` — Mermaid deployment topology (Cosmos DB · FastAPI · LLM provider switch · 5 client platforms) | ⬜ Not started |

### Phase H — Security architecture & threat model (STRIDE)

| ID | Artifact | Status |
|---|---|---|
| **H1** | `docs/security/threat-model.md` — STRIDE threats per trust boundary (Client ↔ FastAPI ↔ Cosmos ↔ LLM provider) | ⬜ Not started |
| **H2** | `docs/paper/figures/trust-boundaries.md` — Mermaid trust-boundary diagram (data crossing each boundary; what is signed/encrypted) | ⬜ Not started |
| **H3** | `docs/security/secrets-inventory.md` — `COSMOS_KEY`, `AZURE_OPENAI_KEY`, `MAIVE_PLATFORM_TOKEN` (planned); rotation owner, store, exposure | ⬜ Not started |
| **H4** | Mitigations table extending H1 — every threat → (a) implemented (cite file), (b) planned (cite plan ID), or (c) accepted-risk (cite DEC) | ⬜ Not started |
| **H5** | [docs/decisions.md](decisions.md) DEC-011 — Security architecture and threat model | 🟡 Placeholder seeded |

### Phase I — Responsible AI specification

| ID | Artifact | Status |
|---|---|---|
| **I1** | `docs/security/rai-policy.md` — scope (astronomy only), prohibited content, provenance requirement (RAG citations), refusal language | ⬜ Not started |
| **I2** | `docs/paper/figures/rai-pipeline.md` — Mermaid sequence: `request → input validator → topic classifier (embedding gate) → prompt-injection heuristics → multi-agent → output validator → audit write → response`; new §15 "Responsible AI" in extended paper | ⬜ Not started |
| **I3** | Astronomy-corpus centroid spec (in I1) — built from mean embedding of ≥50 NASA chunks; rebuilt at every `ingest_knowledge` run; cosine threshold τ tuned against held-out off-topic set | ⬜ Not started |
| **I4** | Abuse / overuse controls catalog (in I1) — per-session call cap, per-user daily quota, token budget, repeated-question detector, prompt-injection regex set; each control has threshold + counter location + refusal message | ⬜ Not started |
| **I5** | [docs/decisions.md](decisions.md) DEC-012 — Responsible AI guardrail pipeline | 🟡 Placeholder seeded |

### Phase J — Audit & evidence storage

| ID | Artifact | Status |
|---|---|---|
| **J1** | New section in [plan/architecture.md](../plan/architecture.md) — Cosmos container `bot_audit` (partition `/session_id`); fields: `id, session_id, user_id, timestamp, request_payload, response_payload, guardrail_verdicts[{stage,verdict,score,rule_hit}], provider, model, prompt_tokens, completion_tokens, latency_ms, condition` | ⬜ Not started |
| **J2** | `docs/security/audit-policy.md` — retention, no-PII, append-only | ⬜ Not started |
| **J3** | Audit ↔ telemetry linkage spec — telemetry `bot_request` event stores `audit_id`; audit row is canonical (no double-storing payloads) | ⬜ Not started |
| **J4** | [docs/decisions.md](decisions.md) DEC-013 — `bot_audit` container is canonical RAI/security evidence store | 🟡 Placeholder seeded |

### Phase K — Verification & validation gate catalog (V right arm)

| ID | Artifact | Status |
|---|---|---|
| **K1** | `docs/security/security-test-cases.md` — reuse thesis Section 4 ST-1..4 with new MAIVE IDs (`ST-OBJ-INTEG`, `ST-SEC-DIST`, `ST-PEN`, `ST-NETMU`); each adds backend file under test, expected outcome, status | ⬜ Not started |
| **K2** | Backend security test catalog (extends K1) — rate-limit enforcement, identify-endpoint replay, prompt-injection refusal, off-topic refusal, audit-write, secret-leak in response | ⬜ Not started |
| **K3** | RAI validation test catalog (extends K1) — 50 astronomy true-positives, 50 off-topic true-negatives, 20 prompt-injection prompts, 10 repeated-question patterns; held-out set in `data/rai_eval/` | ⬜ Not started |
| **K4** | V-Model right-arm trace columns (in K1) — every test → its left-arm requirement (RQ / CR / DEC); closes the V | ⬜ Not started |
| **K5** | Update extended paper §3 — embed G2 matrix + K1–K4 test summary | ⬜ Not started |

### Phase L — Cross-link discipline + reconciliation (closes F8)

| ID | Artifact | Status |
|---|---|---|
| **L1** | `# Documented in: docs/paper/maive-systems-engineering-extended.md#<section>` headers in ~5 backend files (`user.py`, `bot.py`, `health.py`, `llm_provider.py`, `knowledge_ingestion.py`) | ⬜ Not started |
| **L2** | `# Verified by: docs/security/security-test-cases.md#<test-id>` headers where applicable | ⬜ Not started |
| **L3** | Update [docs/status.md](status.md) and this file — reflect Phases G–L; mark prior F4 stub superseded by G/I/J/K | ✅ Done (2026-04-28) |
| **L4** | Reconcile stale entries — Phase A–F tables in this file still showed ⬜/🟡 but are actually ✅; remove duplicate "in progress" lines from `docs/status.md` | ✅ Done (2026-04-28) |

### Sequencing (Phases G–L)

1. **G1 + G3 + G5** parallel
2. **G2 + G4** depend on G1/G3
3. **H1–H5** parallel with G (independent track)
4. **I1–I5** depend on H1–H2 (uses trust boundaries)
5. **J1–J4** depend on I (audit schema needs guardrail verdict shape from I2)
6. **K1–K5** depend on G2 + H4 + I4 + J1
7. **L1–L4** last — reconciles everything and closes the cross-link discipline gate

### Verification gates (Phases G–L)

1. All `docs/paper/figures/*.md` Mermaid blocks render in VS Code preview
2. No orphan rows in `traceability-matrix.md` and `security-test-cases.md`
3. STRIDE coverage — all 6 categories present in `threat-model.md` with verdict columns
4. RAI policy completeness — at least 3 refusal categories (off-topic, harmful, prompt-injection) with example refusal text
5. Decision log — DEC-011, DEC-012, DEC-013 added with `Date: 2026-04-28`
6. Cross-link audit — `grep -rn "Documented in:" src/backend/app | wc -l` ≥ 5
7. Status parity — `docs/status.md` phase table includes G–L rows; this file's Phase A–F tables updated to ✅
8. Doc-only constraint — no behavioral source code change in this plan

### Decisions captured (Phases G–L)

- **STRIDE** as threat-modeling vocabulary (industry standard, easy to audit)
- **`bot_audit` is the canonical RAI/security evidence store** — telemetry events reference it by ID, do not duplicate payloads
- **Astronomy-only enforcement is multi-layered** (embedding gate + prompt rules + output validator + abuse controls)
- **No PII** in any audit/telemetry/request payload (re-affirms DEC-009)
- **Security test cases reuse thesis Section 4 verbatim** and extend with backend-specific cases
- **`docs/security/` standalone files** cross-linked from the paper (vs. embedded only)
- **V-Model figure uses thesis lifecycle phases** as canonical; Clean Architecture mapping shown as a separate "implementation lens" diagram in §4
- **`bot_audit` partition key `/session_id`** (matches research-session granularity)

### Out of scope (Phases G–L)

- Any **runtime code** for guardrails, audit container, rate limits — separate **Phase M — RAI/Security implementation** plan
- Azure AI Content Safety integration
- Auth (Entra ID) — already future-work per AGENTS.md
- Live verification runs of `/api/health` against Cosmos+Ollama (separate operational task)

---

## Phase N — Bilingual content & experience: English / Spanish (added 2026-04-28)

> **Goal.** Make the learner's preferred language a first-class field that propagates from client → session → agents → response → telemetry/audit, so RQ analyses can be split by language and Spanish-speaking participants get a fully Spanish experience (UI, static help, RAG, AI bot).

### Steps

| ID | Change | Layer / files |
|---|---|---|
| **N1** | Add `preferred_language: str = "en"` to `User` entity + `IdentifyUserDTO` + `UserResponseDTO` | [src/backend/app/domain/entities/user.py](../src/backend/app/domain/entities/user.py), [src/backend/app/application/dtos/user_dtos.py](../src/backend/app/application/dtos/user_dtos.py) |
| **N2** | Add `language: str = "en"` to `Session` entity + Session create/response DTOs (per-session override of user default) | [src/backend/app/domain/entities/session.py](../src/backend/app/domain/entities/session.py), session DTOs |
| **N3** | Add `language: str \| None = None` to `BotAskRequest`; resolve effective language as `request.language ?? session.language ?? user.preferred_language ?? "en"`; echo back as `BotAskResponse.language` | [src/backend/app/api/routes/bot.py](../src/backend/app/api/routes/bot.py) |
| **N4** | Split agent system prompts into `<agent>_en.md` + `<agent>_es.md`; loader picks file by language; coordination agent passes language down to user-modeling, content-curation, assessment | `src/backend/app/infrastructure/agents/*.py` + prompt files |
| **N5** | Static help content: add `language` field to JSON schema + Cosmos query filter; seed `data/help_content/<planet>/<lang>/*.json` | seed CLI + `HelpContentRepository` + use case |
| **N6** | RAG: tag chunks with `language` at ingest; folder layout `data/nasa/<lang>/<body>.md`; filter retrieval by effective language; fallback rule: if no chunks in target language, retrieve EN chunks but instruct LLM to answer in target language and mark `language_fallback=true` | `app/cli/ingest_knowledge.py`, embedding store query |
| **N7** | Frontend i18n on `LearnerPage`: lightweight context (or `react-i18next`); `en.json`/`es.json` resources; language selector; persist to `localStorage`; pass to `identify`, `createSession`, `askBot` | [src/frontend/src/pages/LearnerPage.tsx](../src/frontend/src/pages/LearnerPage.tsx), [src/frontend/src/api/client.ts](../src/frontend/src/api/client.ts), `src/frontend/src/i18n/` (new) |
| **N8** | Set `<html lang>` dynamically; researcher pages add `language` column (read-only) | [src/frontend/index.html](../src/frontend/index.html), researcher pages |
| **N9** | Telemetry + (Phase J1) `bot_audit` write resolved `language` per event/request | telemetry DTOs + Phase J1 schema |
| **N10** | Backfill: existing `User`/`Session` documents default to `language="en"` (no migration script — Pydantic default handles read; idempotent re-write on update) | repo layer |
| **N11** | DEC-014 — Bilingual support model (resolution order, fallback rules, human-translated agent prompts, no runtime MT) | [docs/decisions.md](decisions.md) |
| **N12** | Update [docs/plan.md](plan.md), [docs/status.md](status.md), [docs/paper/maive-systems-engineering-extended.md](paper/maive-systems-engineering-extended.md) §11 + add `docs/paper/figures/language-flow.md` (Mermaid: client → effective-language resolution → agent/static path → response) | docs only |

### Sequencing (Phase N)

1. **N1 + N2** parallel — data model
2. **N3** depends on N1+N2
3. **N4 + N5 + N6** parallel after N3 — translation + content
4. **N7 + N8** parallel after N3 (frontend can stub against fixed `language` first)
5. **N9** depends on N3
6. **N10 + N11 + N12** last — closes the loop

### Verification (Phase N)

1. `POST /api/users/identify` accepts and persists `preferred_language="es"`; round-trips on `GET /api/users/{id}`
2. `POST /api/sessions` with `language="es"` overrides user default
3. `POST /api/bot/ask` with `condition="non-adaptive-vr"` returns Spanish `body_text` from a Spanish help-content row
4. `POST /api/bot/ask` with `condition="maive"` returns Spanish answer; system-prompt swap verified via `bot_audit` (planned)
5. Ingest `data/nasa/es/marte.md`; Spanish question returns Spanish-cited answer
6. Frontend selector switches all UI strings; reload preserves choice; API calls carry `language=es`
7. Researcher `UsersPage` shows `language` column
8. `BotAskResponse.language` always reflects the actually-used language (so client can render correctly even on fallback)
9. Telemetry rows in a mixed-language session correctly attribute each event to its language
10. DEC-014 dated 2026-04-28 present in [docs/decisions.md](decisions.md)

### Decisions captured (Phase N — DEC-014, Accepted 2026-04-28)

- **Resolution order:** request override → session → user preference → `"en"` default
- **Agent prompts are human-translated** by PhD owner (Francia Riesco, bilingual); no runtime MT, no third-party translation service
- **RAG language fallback:** if no chunks exist in target language, retrieve English chunks but instruct LLM to *answer in target language*; mark response with `language_fallback=true` for audit
- **Static help content** must exist in **both languages** before a planet/section is released for a Spanish session (enforced by seeder check, not at request time)
- **No machine-translation API dependency** introduced in Phase N (small dependency surface)
- **`es` neutral** (LatAm/EU-agnostic) for v1; locale tag deferred until pilot data shows confusion
- **Default language on first contact:** all clients default to `"en"`; learner explicitly picks Spanish via in-experience selector. Browser `Accept-Language` is not auto-applied (consistent across the 5 platforms; consent step first)
- **Concept inventory + ARCS in Spanish:** validated published Spanish versions exist; sourcing tracked by Francia. Citations added to extended paper §10 + References before data collection

### Out of scope (Phase N)

- Auto language detection from query text (rely on explicit selection)
- Right-to-left languages
- Voice / TTS in Spanish (separate concern)
- Translation of thesis instruments (use validated published versions externally)
- Researcher dashboard internationalization (researcher-facing pages stay English)
