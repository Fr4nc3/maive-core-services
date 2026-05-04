# Backend Sample-Code Review Plan

> Permanent review plan for comparing the local `data/sample_code` reference
> material with the MAIVE backend. Use this whenever backend architecture,
> repository wiring, bot/RAI behavior, or provider/agent patterns change.

Last baseline run: 2026-05-04

## Purpose

`data/sample_code` is a reference-quality benchmark for well-defined backend
API/service practices. It demonstrates good patterns for code quality,
modularity, ease of use, scalable growth, and safe growth. The sample projects
can inspire implementation decisions, but they must not override MAIVE rules
for Clean Architecture, the unified bot endpoint, keyless Azure authentication,
Cosmos DB access-pattern discipline, or DEC-019 RAI audit guarantees.

`data/sample_code` is ignored by git in this repository. Treat it as local
reference material, not a versioned project dependency.

Before merge to `main`, remove code that is not part of the approved MAIVE
Core Services implementation. Temporary sample/reference code can support
implementation decisions, but it must not remain in the product path unless it
is intentionally adopted, reviewed, and documented as MAIVE code.

## Quality Attributes

This review validates that MAIVE Core Services embodies these quality attributes:

- **Code quality and reliability:** Validation, typed DTOs, consistent error handling, predictable responses, lint/format/test gates, no hidden PII or secret shortcuts.
- **Well-defined backend API services:** Clear contracts, DTO boundaries, predictable route behavior, reusable service/use-case orchestration.
- **Modularity:** Isolated layers, repository ports, registry/factory construction, no cross-layer shortcuts.
- **API and developer ease of use:** Consistent commands, predictable dependency wiring, clear API contracts, stable client payloads, easy onboarding.
- **Scalable growth:** More agents, providers, repositories, and clients without broad rewrites.
- **Ease of modification:** Localized, testable changes documented in the findings register.
- **Safe to grow:** Preserve unified bot endpoint, platform identity model, no-PII rule, Cosmos DB access-pattern discipline, RAI audit requirements, and keyless Azure auth.

## Review Inputs

### MAIVE Sources

- `src/backend/app/dependencies.py` - dependency entry points and singleton
  repository construction.
- `src/backend/app/config.py` - non-secret settings and keyless Azure auth
  policy.
- `src/backend/app/domain/entities/` - pure domain models.
- `src/backend/app/domain/interfaces/` - repository ports.
- `src/backend/app/application/dtos/` - API/application DTO boundary.
- `src/backend/app/application/use_cases/` - business orchestration.
- `src/backend/app/infrastructure/persistence/cosmos_db/` - Cosmos DB
  repository implementations.
- `src/backend/app/infrastructure/ai/registry.py` - LLM provider registry.
- `src/backend/app/infrastructure/rai/` - RAI guardrail modules.
- `src/backend/app/api/routes/bot.py` - unified bot endpoint.
- `src/backend/app/cli/qa_audit.py` - canonical QA runner.
- `src/backend/tests/rai/` - RAI regression suite.

### Sample-Code References

- `data/sample_code/python_agent_framework_dev_template-main/src/libs/application/application_context.py`
  - dependency lifetime reference.
- `data/sample_code/python_agent_framework_dev_template-main/src/libs/agent_framework/agent_builder.py`
  - fluent agent construction reference.
- `data/sample_code/python_agent_framework_dev_template-main/src/libs/agent_framework/middlewares.py`
  - middleware and instrumentation reference.
- `data/sample_code/python_agent_framework_dev_template-main/src/libs/agent_framework/cosmos_checkpoint_storage.py`
  - typed Cosmos repository reference.
- `data/sample_code/python_agent_framework_dev_template-main/src/utils/agent_telemetry.py`
  - cautionary reference: persistence inside a generic `utils/` layer should
    not be copied into MAIVE.
- `data/sample_code/content-processing-solution-accelerator/`
  - multi-component API, worker, and workflow organization reference.
- `data/sample_code/agentic-applications-for-unified-data-foundation-solution-accelerator/`
  - agentic API and data exploration reference.
- `data/sample_code/prototypes-main/`
  - prototype-only reference; do not use as backend architecture precedent.

## Review Tasks

1. Discovery baseline
   - Inventory relevant sample projects and current MAIVE backend layers.
   - Capture reusable ideas and explicitly reject incompatible patterns.

2. Clean Architecture boundary audit
   - Domain must not import infrastructure, API, or application code.
   - Application use cases should depend on domain interfaces, not concrete
     infrastructure.
   - API routes should stay thin and delegate orchestration to use cases.
   - Infrastructure should implement domain ports and avoid API dependencies.

3. Pattern comparison audit
   - Compare MAIVE's current dependency functions with the sample `AppContext`
     lifetime pattern.
   - Compare MAIVE agent construction with the sample `AgentBuilder` pattern.
   - Compare MAIVE RAI/audit behavior with sample middleware instrumentation.
   - Classify each pattern as `Already Covered`, `Adopt Later`, `Reject`, or
     `Needs Fix`.

4. Cosmos repository review
   - Every Cosmos repository must inherit from `BaseCosmosRepository`.
   - Queries with user input must be parameterized.
   - Datetime fields must be serialized consistently.
   - Cosmos metadata must be stripped before entity validation.
   - Partition keys should be supplied when known.

5. API and use-case review
   - Route handlers should get dependencies, create the use case, and return
     `await use_case.execute(...)` when feasible.
   - Business rules should not accumulate in routes.
   - Use cases should not directly construct Cosmos repository implementations.
   - No client-facing endpoint should bypass `POST /api/bot/ask`.

6. RAI and bot pipeline review
   - Verify DEC-019: input validation, topic gate, prompt-injection check,
     system prompt, agent/static response, output validation, and audit row.
   - Audit rows must not store raw query text or raw LLM output.
   - Audit writes must never break the request.
   - Broad `except Exception` remains allowed only in approved audit-write
     best-effort blocks.

7. Registry and factory review
   - LLM provider construction must go through `LLMProviderRegistry.build(...)`.
   - New provider, agent, or repository branching should become registry code
     only when real branching complexity exists.
   - No `provider == "..."` or `elif ... provider` branches should leak into
     application or route code.

8. Configuration and secrets review
   - No `COSMOS_KEY`, `AZURE_OPENAI_KEY`, `cosmos_key`, or `azure_openai_key`.
   - Non-secret configuration belongs in `Settings`.
   - Azure service authentication uses `DefaultAzureCredential`, managed
     identity, and RBAC.

9. Findings register
   - Record each result as `Pass`, `Needs Fix`, `Adopt Later`, or `Reject`.
   - Link every finding to a MAIVE file and, when useful, the sample-code
     pattern that informed it.

10. Main merge cleanup gate
    - Classify implementation code as MAIVE Core Services, temporary
      reference code, or reject.
    - Remove temporary/reference code before merge to `main` unless it has
      been intentionally adopted into MAIVE Core Services.

## Commands

Run from the repository root unless a command begins with `cd src/backend`.

```powershell
cd src/backend
uv run python -m app.cli.qa_audit all
uv run ruff check .
uv run pytest tests/rai/ -v
uv run pytest tests/rai/ --cov=app/application --cov=app/infrastructure/rai --cov-fail-under=80
```

Targeted boundary checks:

```powershell
rg -n "from app\.infrastructure" src/backend/app/domain
rg -n "from app\.infrastructure\.persistence" src/backend/app/api
rg -n "from app\.infrastructure" src/backend/app/application
rg -n "httpx|requests|azure\.cosmos|openai" src/backend/app/domain/entities
rg -n "provider\s*==\s*[\"']|elif.*provider" src/backend/app
rg -n "/api/(agents/help|static-bot)|evaluate_session" src/backend/app/api
```

## Baseline Findings - 2026-05-04

Canonical command run from `src/backend`:

```powershell
uv run python -m app.cli.qa_audit all
```

Result: 33/41 checks passed. The command exited 1, so this is the current
implementation backlog before the backend can be called clean by the full QA
gate.

| ID | Status | Area | Evidence | Recommended Action |
|---|---|---|---|---|
| QAR-001 | Needs Fix | Unified bot / RAI | `src/backend/app/api/routes/bot.py` constructs `get_coordination_agent()` and calls `agent.evaluate_session(...)` directly on the AI path. `qa_audit rai-check` failed `bot.py uses BotPipelineUseCase` and `bot.py AI path does NOT call agent.evaluate_session directly`. | Route the AI path through `BotPipelineUseCase` and keep static/AI behavior inside the DEC-019 pipeline. Coordinate with `@maive-rai` before editing. |
| QAR-002 | Needs Fix | Clean Architecture | Targeted boundary search found `src/backend/app/api/routes/health.py` importing `app.infrastructure.persistence.cosmos_db.client`. | Move Cosmos health-check construction behind `app/dependencies.py` or an application-level health use case so routes do not import persistence directly. |
| QAR-003 | Needs Review | Clean Architecture / RAI | Targeted boundary search found `src/backend/app/application/use_cases/bot_pipeline_use_case.py` importing `app.infrastructure.rai`. | Decide whether RAI guardrails are intentionally infrastructure-owned or should expose application/domain ports. If DEC-019 accepts this exception, encode it in QA guidance; otherwise refactor. |
| QAR-004 | Needs Fix | Library currency | Ruff failed `UP042`: `TelemetryEventType` inherits from both `str` and `Enum` in `src/backend/app/domain/entities/telemetry.py`; ruff recommends `StrEnum`. | Requires explicit permission because domain entity edits are protected by repository rules. |
| QAR-005 | Needs Fix | Time handling | `datetime.utcnow()` remains in `src/backend/app/application/use_cases/help_content_use_cases.py` and `src/backend/app/application/use_cases/session_use_cases.py`. | Replace with timezone-aware `datetime.now(UTC)` and adjust imports. |
| QAR-006 | Needs Fix | Exception handling | Broad `except Exception` remains in `agent_action_repository.py`, `help_content_repository.py`, and `task_attempt_repository.py`. | Catch `CosmosResourceNotFoundError` for not-found read paths instead of swallowing all exceptions. |
| QAR-007 | Needs Fix | Type safety | `mypy` reports missing type arguments for generic `dict` across several domain entities and DTOs. | Requires explicit permission for domain entity changes; DTO fixes can be handled separately. |
| QAR-008 | Needs Fix | Coverage | RAI coverage gate reported total coverage of 29%, below the 80% threshold for `app/application` + `app/infrastructure/rai`. | Add or scope tests intentionally. Test edits require explicit user permission under MAIVE rules. |
| QAR-009 | Needs Fix | RAI evidence | `phd-check` did not find required RAI citation tokens (`Lakera`, `garak`, `OWASP`, `Keller`, `NIST`, `MITRE`) in `src/backend/app/infrastructure/rai/`. | Add concise evidence comments/docstrings in RAI modules or adjust the checker if citations belong only in docs. Coordinate with `@maive-rai`. |
| QAR-010 | Pass | Domain purity | Targeted search found no `httpx`, `requests`, `azure.cosmos`, or `openai` imports in `src/backend/app/domain/entities/`. | Preserve this boundary. |
| QAR-011 | Pass | Registry pattern | Provider literal and `elif provider` search found only `qa_audit.py` pattern definitions and `infrastructure/ai/registry.py` documentation. | Preserve registry-based provider construction. |

## Sample-Code Pattern Decisions

| Pattern | Decision | Rationale |
|---|---|---|
| AppContext-style DI lifetimes | Adopt Later | Useful if MAIVE grows multiple agent families or persistence backends. Current `dependencies.py` singleton functions are simpler and adequate. |
| Fluent `AgentBuilder` | Adopt Later | Could reduce boilerplate after agent construction becomes dynamic. Do not introduce before an actual branching problem exists. |
| Middleware instrumentation | Adopt Later | Useful for tracing and timing, but must not replace DEC-019 guardrails or audit rows. |
| Typed Cosmos repository base | Already Covered | MAIVE already has `BaseCosmosRepository`; preserve it. |
| Telemetry persistence in `utils/` | Reject | Persistence belongs in infrastructure repositories and application orchestration, not a generic support module. |
| Prototype scripts as architecture precedent | Reject | Prototype code can inspire experiments but should not define backend layering. |

## Review Cadence

Run this review before merging work that touches:

- `src/backend/app/api/routes/bot.py`
- `src/backend/app/application/use_cases/bot_pipeline_use_case.py`
- `src/backend/app/infrastructure/rai/`
- `src/backend/app/dependencies.py`
- `src/backend/app/config.py`
- `src/backend/app/infrastructure/persistence/cosmos_db/`
- any new provider, agent, repository, or backend route
- any temporary/reference implementation inspired by `data/sample_code`

Update the findings table after each audit run. Do not remove closed findings;
change their status to `Pass` and keep the evidence trail.