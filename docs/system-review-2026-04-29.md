# MAIVE — System Review

> **Date:** 2026-04-29
> **Author:** @maive-lead (consolidated from a working session)
> **Scope:** Services, implementation plan, infrastructure, current status,
> API surface, telemetry collection, and the three research questions.
> **Audience:** PhD committee, advisors, contributing engineers.
>
> This is a snapshot. Living counterparts:
> [`docs/status.md`](status.md) (running status board) and
> [`docs/plan.md`](plan.md) (current plan).

---

## 1. The three research questions

Per [`AGENTS.md`](../AGENTS.md) and the working thesis
([`docs/PhD-Astronomy World - Work In progress- francia-riesco.md`](PhD-Astronomy%20World%20-%20Work%20In%20progress-%20francia-riesco.md)).

| RQ | Question | Primary instrument | Comparison |
|---|---|---|---|
| **RQ1** | **Conceptual learning gains** — does adaptive multi-agent VR (`maive`) produce larger normalized learning gains than non-adaptive VR (`non-adaptive-vr`)? | Concept-inventory pre/post → `Assessment` | Between-condition |
| **RQ2** | **Engagement & attitudes** — do learners report higher motivation (ARCS: Attention / Relevance / Confidence / Satisfaction) and exhibit higher behavioral engagement (lower idle, higher persistence/time-on-task) under MAIVE? | `ARCSSurveyResponse` + `QualitativeFeedback` + behavioral `TelemetryEvent` | Between-condition + within-session change |
| **RQ3** | **Problem-solving & transfer** — does MAIVE improve solver behavior (steps, hints, errors, retries, trajectory revisions) and transfer to a follow-up open-ended challenge? | `TaskAttempt` + `Assessment(type="transfer")` + `ClassifierPrediction` | Between-condition + classifier AUC |

The contrast lives on a single field:
[`Session.condition ∈ {"maive", "non-adaptive-vr"}`](../src/backend/app/domain/entities/session.py).
The same `POST /api/bot/ask` endpoint serves both arms; routing happens
server-side per `condition`.

---

## 2. Service surface (backend topology)

| Layer | Module count | Notes |
|---|---|---|
| API routes (`app/api/routes/`) | 12 | All wired via DI in [`app/dependencies.py`](../src/backend/app/dependencies.py) |
| Use cases (`app/application/use_cases/`) | 11 | Includes [`bot_pipeline_use_case.py`](../src/backend/app/application/use_cases/bot_pipeline_use_case.py) (Phase R) |
| DTOs (`app/application/dtos/`) | 10 | |
| Domain entities (`app/domain/entities/`) | 11 | New `BotAudit` entity (Phase R) |
| Domain interfaces (`app/domain/interfaces/`) | 11 | New `BotAuditRepository` port |
| Cosmos repositories (`app/infrastructure/persistence/cosmos_db/`) | 13 + base + client | All inherit `BaseCosmosRepository` |
| Multi-agent layer (`app/infrastructure/agents/`) | 4 | Coordination · UserModeling · ContentCuration · Assessment |
| AI / LLM (`app/infrastructure/ai/`) | 6 | `LLMProvider` port + `OllamaProvider` + `AzureFoundryProvider` + `LLMProviderRegistry` (Phase P1) |
| **RAI guardrails (`app/infrastructure/rai/`)** | **7** | `input_validator` · `topic_gate` · `prompt_injection` · `system_prompt` · `output_validator` · `audit` · `errors` |

### Endpoint inventory (29 routes)

#### Identity & session lifecycle
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/users/identify` | Idempotent identify by `(platform, platform_user_id)` |
| POST · GET | `/api/users` · `/api/users/{id}` | Create / fetch / list |
| POST · GET · PATCH | `/api/sessions` · `/api/sessions/{id}` | Start / read / mutate |

#### Unified bot (the experimental contrast)
| Method | Path | Purpose | RQ link |
|---|---|---|---|
| POST | [`/api/bot/ask`](../src/backend/app/api/routes/bot.py) | Single endpoint; routes by `session.condition` to the RAI pipeline (`maive`) or static `help_content` (`non-adaptive-vr`). Writes `bot_audit` row both paths. | RQ1 / RQ2 (treatment delivery) |

#### Research-data ingestion (the measurement surface)
| Method | Path | Captures | RQ link |
|---|---|---|---|
| POST · GET | `/api/telemetry` · `/api/telemetry/{session_id}` | All 24 `TelemetryEventType` events | **RQ2 + RQ3** |
| POST · PATCH · GET | `/api/task_attempts` · `/api/task_attempts/{session_id}` | Per-attempt rollups | **RQ3** |
| POST · GET | `/api/assessments` · `/api/assessments/{id}` | Pre / post / transfer concept inventory | **RQ1 + RQ3** |
| POST · GET | `/api/arcs_surveys` · `/api/arcs_surveys/{session_id}` | ARCS Likert | **RQ2** |
| POST · GET | `/api/qualitative_feedback` · `/api/qualitative_feedback/{session_id}` | Open-text reflections | **RQ2 (qual)** |
| POST · GET | `/api/classifier_predictions` · `/api/classifier_predictions/{session_id}` | Predicted success per session | **RQ3 (model)** |
| POST | `/api/agents/adapt` | Trigger agent adaptation; produces `AgentAction` records | RQ1 (mechanism) |

#### Operations
| Method | Path | Purpose |
|---|---|---|
| GET · POST · PATCH | `/api/help_content` · `/api/help_content/planets` · `/api/help_content/{planet}/{content_id}` | Control-arm static content |
| GET | `/api/health` · `/api/health/llm` · `/api/health/cosmos` | Liveness / readiness |

---

## 3. Telemetry collection

### `TelemetryEvent` taxonomy — 24 event types in 8 groups
[`src/backend/app/domain/entities/telemetry.py`](../src/backend/app/domain/entities/telemetry.py),
schema in [`plan/telemetry-model.md`](../plan/telemetry-model.md).

| Group | Events | RQ feed |
|---|---|---|
| Help interactions | `HELP_REQUESTED` · `HELP_DELIVERED` · `HELP_DISMISSED` · `HELP_FOLLOWED` | RQ2 + RQ1 |
| Section navigation | `SECTION_ENTERED` · `SECTION_EXITED` | RQ2 |
| Task interaction | `TASK_STARTED` · `TASK_STEP_COMPLETED` · `TASK_COMPLETED` · `TASK_ABANDONED` | RQ3 |
| Errors & retries | `ERROR_COMMITTED` · `RETRY_ATTEMPTED` | RQ3 |
| Assessment | `QUIZ_ANSWER_SUBMITTED` · `SURVEY_COMPLETED` | RQ1 / RQ2 anchor |
| Agent interaction | `AGENT_PROMPT_DISPLAYED` · `_DISMISSED` · `_FOLLOWED` | RQ1 |
| Session lifecycle | `SESSION_PAUSED` · `_RESUMED` · `MODULE_ENTERED` · `_EXITED` | RQ2 |
| Idle detection | `IDLE_DETECTED` (>60 s) | RQ2 |

### Per-event context fields
`section` (planet) · `content` (topic) · `help_text` · `bot_type ∈ {"hardcoded","ai"}` · event-specific `payload`. Detailed payload schema in
[`plan/telemetry-model.md §2.2`](../plan/telemetry-model.md).

### RQ → endpoint → analysis traceability matrix

| RQ slice | Source endpoint | Source entity / container | Cosmos PK | Analysis target |
|---|---|---|---|---|
| RQ1 normalized gain | `/api/assessments` (`pre`, `post`) | `Assessment` | `/user_id` | Paired t-test by `condition` |
| RQ1 agent effectiveness | `/api/agents/adapt` + `/api/telemetry?event=AGENT_PROMPT_*` | `AgentAction` + `TelemetryEvent` | `/session_id` | Logistic on follow-rate by `agent_role` |
| RQ2 ARCS scores | `/api/arcs_surveys` | `ARCSSurveyResponse` | `/session_id` | MANOVA by `condition` |
| RQ2 behavioral engagement | `/api/telemetry` (`IDLE_DETECTED`, `RETRY_ATTEMPTED`, `SECTION_*`) | `TelemetryEvent` | `/session_id` | Idle %, time-on-task by `condition` |
| RQ2 qualitative | `/api/qualitative_feedback` | `QualitativeFeedback` | `/session_id` | Thematic coding |
| RQ3 problem-solving | `/api/task_attempts` + telemetry rollups | `TaskAttempt` | `/session_id` | Step time, hint freq, retries |
| RQ3 transfer | `/api/assessments?type=transfer` | `Assessment` | `/user_id` | Group comparison + rater-IRR (κ) |
| RQ3 classifier | `/api/classifier_predictions` | `ClassifierPrediction` | `/session_id` | AUC / calibration |
| Cross-cutting (RAI) | every `/api/bot/ask` | `BotAudit` (DEC-013/019) | `/session_id` | RAI compliance + per-stage audit |

---

## 4. Implementation plan — phase status

### Active (template-conformant) phases — done
- ✅ Phase R — RAI bot pipeline (DEC-019)
- ✅ Phase W — Granular sub-agent surface (DEC-020)
- ✅ Phase S — Help_content seed (operator step S3 pending)
- ✅ Phase P4 — Narrow exception handling
- ✅ Phase V — Verification gate (V5 / V6 operator-pending)

### In-flight today (this session)
- ✅ Phase PD — plan template + history + AGENTS.md cross-link
- ✅ Phase QA — Rubric 6 (`pillars-check`) + Rubric 7 (`phd-check`) + 94-file pillar header sweep

### Pre-template phases (kept verbatim, migrated lazily)
A–F · G–L · N · O · P1 · Q.

### Pending phases (queued)

| Phase | Description | Owner | DEC |
|---|---|---|---|
| **QA4–6** | Update maive-qa instructions / agent / checklist for new rubrics | @maive-qa | DEC-023 |
| **KV** | Replace Key Vault with App Configuration + Managed Identity | @maive-deploy | DEC-021 (supersedes DEC-018) |
| **OL** | Ollama static-IP egress (NAT Gateway + Standard Public IP) | @maive-deploy | DEC-022 |
| **GD** | Usage guides (using-maive-qa.md + implementing-maive-feature.md) | @maive-lead | — |
| **DOC** | Prepend DEC-021 / 022 / 023 + status update | @maive-lead | DEC-021 / 022 / 023 |
| **RX** *(proposed)* | Research-data integrity (batch telemetry, export, dup-guards, auto-emit `HELP_DELIVERED`) | @maive-research | new |

Pre-template tracks still open per [`docs/status.md`](status.md): G (V-Model figures), H (STRIDE), I (RAI policy expansion), J (audit policy), K (V&V catalog), L (cross-link headers), N (bilingual EN / ES), X (rate limit + Content Safety).

---

## 5. Infrastructure (current Bicep)

[`infra/`](../infra/) layout — 1 root + 6 modules.

```
infra/main.bicep
infra/modules/
  ├─ ai_foundry.bicep      ✅ AI Foundry + chat / embedding deployments
  ├─ appservice.bicep      ✅ B1 App Service (frontend)
  ├─ containerapp.bicep    ✅ Container Apps env + backend (system MI)
  ├─ cosmos.bicep          ✅ Serverless + Vector + bot_audit container (PK /session_id)
  ├─ keyvault.bicep        ⚠️ MARKED FOR REMOVAL (DEC-021)
  └─ monitoring.bicep      ✅ Log Analytics + Application Insights
```

### Deviations from target architecture

| Issue | Where | Fix planned |
|---|---|---|
| **Key Vault still wired** in [`main.bicep`](../infra/main.bicep) → containerapp + outputs | [`main.bicep`](../infra/main.bicep) | Phase KV — replace with `appconfig.bicep` + Managed Identity |
| **No NAT Gateway / static egress** for Ollama (dev path leaks via dynamic IP) | Container Apps env | Phase OL — add `networking.bicep` (VNet + Standard SKU Public IP + NAT) |
| **Cosmos `disableLocalAuth: false`** | [`cosmos.bicep`](../infra/modules/cosmos.bicep) | Flip to `true` once App Configuration + MI auth ships |
| **`publicNetworkAccess: 'Enabled'`** on Cosmos | [`cosmos.bicep`](../infra/modules/cosmos.bicep) | Defer (Private Endpoint phase out of scope per AGENTS.md) |
| **Single region, no zone-redundancy** | [`cosmos.bicep`](../infra/modules/cosmos.bicep) | OK for thesis; not production |

### Operator steps still pending (V5 / V6 / S3)
- `docker compose up` smoke test ([`docs/RUNLOCAL.md`](RUNLOCAL.md) Path B)
- `azd provision --preview` against the real subscription
- `seed_help_content` against live Cosmos

---

## 6. Current status — pre-PR gate (live)

| Check | Result |
|---|---|
| `uv run ruff check .` | **1 error** — pre-existing `UP042` on `TelemetryEventType` (known debt) |
| `uv run pytest tests/rai/ -q` | **42 / 42** ✅ |
| `qa_audit pillars-check` | **2 / 2** ✅ |
| `qa_audit rai-check` | **16 / 16** ✅ |
| `qa_audit phd-check` | **8 / 12** ⚠️ — mypy strict / coverage < 80 % / missing RAI citations |
| `qa_audit if-else-scan` | **5 / 5** ✅ |

### Documentation & decisions
- [`docs/decisions.md`](decisions.md) — DEC-001 through DEC-020 landed; DEC-021 / 022 / 023 pending (Phase DOC).
- [`docs/plan.md`](plan.md) — template-migrated for active phases; pre-template divider in place.
- [`docs/plan-template.md`](plan-template.md), [`docs/plan-history.md`](plan-history.md) — new this session (1 history row).

---

## 7. Gap & risk audit (research-data quality)

| # | Gap | Endpoint(s) affected | Severity | Recommendation |
|---|---|---|---|---|
| 1 | No bulk telemetry POST (each event = 1 HTTP call from VR) | `/api/telemetry` | **High** for VR throughput | Add `POST /api/telemetry/batch` accepting `list[TelemetryCreate]` |
| 2 | No researcher export endpoint | none | **High** for analysis | Add `GET /api/research/export?since=&condition=` (NDJSON streaming), gated by analyst role |
| 3 | `/api/bot/ask` does not auto-emit a `HELP_DELIVERED` `TelemetryEvent` | `bot.py` | **High** — RQ2 will under-count uptake | Inside the use case: emit event after audit row write |
| 4 | ARCS / Qualitative endpoints don't restrict 1-per-session-per-module | `arcs_surveys` · `qualitative_feedback` | Medium — duplicates inflate N | Use case should reject duplicate `(session_id, module_id)` |
| 5 | No `IDLE_DETECTED` server-side validator (clients can spoof) | `telemetry` | Medium — RQ2 integrity | Add domain rule `idle_duration_ms ≥ 60_000` |
| 6 | `Assessment.assessment_type` not enum-checked at API boundary | `assessments` | Medium — RQ1 / RQ3 stratification | Tighten DTO with `Literal["pre","post","transfer"]` |
| 7 | No way to link `ClassifierPrediction` to the `TaskAttempt` it predicts | `classifier_predictions` | Medium — RQ3 evaluation | Add `task_attempt_id` FK |
| 8 | `TelemetryEvent.timestamp` uses `datetime.utcnow()` (naïve) | `telemetry.py` | Low (CI-banned elsewhere) | Switch to `datetime.now(UTC)` |
| 9 | No `/api/sessions/{id}/end` lifecycle hook to compute `total_duration_ms` etc. | `sessions` | Low | Add server-side rollup |
| 10 | `ClassifierPrediction.PK` not in plan | `classifier_predictions` repo | Low | Confirm `/session_id` aligns with telemetry PK |

> Items 1 – 7 should be batched into a new **Phase RX — Research-data
> integrity**, planned with [`plan-template.md`](plan-template.md) and slotted
> ahead of any data collection.

---

## 8. Fitness-to-research scorecard

| Dimension | Score | Notes |
|---|---|---|
| **Coverage** of RQs by entities | 9 / 10 | All 3 RQs have dedicated entities; `BotAudit` adds RAI provenance |
| **Coverage** of RQs by endpoints | 8 / 10 | Missing: batch ingestion, research export |
| **Auditability** | 9 / 10 | DEC-019 audit row on every bot call |
| **Identity privacy** | 10 / 10 | DEC-009: no PII; `(platform, platform_user_id)` + UUID only |
| **Causal contrast** clarity (`condition`) | 10 / 10 | One enum, one route, two paths |
| **Statistical readiness** | 7 / 10 | Stratification + duplicate guards still missing |

---

## 9. Recommended next moves (priority order)

1. **QA4–6** — close the QA pillar gate so future restructures are linted.
2. **DOC** — write DEC-021 / 022 / 023 *before* touching Bicep (gives infra changes a citation anchor).
3. **KV ∥ OL** — paired infra change; both touch `main.bicep` and require an `azd provision --preview` together.
4. **RX** — research-data integrity; should land before any participant data collection.
5. **GD** — usage guides; comes after the QA gate and infra work so guides reference the real surface.

---

## 10. Cross-references

- [`docs/status.md`](status.md) — running status (always read first)
- [`docs/plan.md`](plan.md) — current plan
- [`docs/plan-template.md`](plan-template.md) — strict template for new phases
- [`docs/plan-history.md`](plan-history.md) — restructure log
- [`docs/decisions.md`](decisions.md) — architectural decisions (DEC-NNN)
- [`docs/rai-policy.md`](rai-policy.md) · [`docs/threat-model.md`](threat-model.md)
- [`plan/architecture.md`](../plan/architecture.md) · [`plan/telemetry-model.md`](../plan/telemetry-model.md)
- [`AGENTS.md`](../AGENTS.md) — workspace-wide rules of engagement
