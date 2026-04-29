---
description: MAIVE QA rubric — encoded grep patterns and pass/fail rules. Use whenever auditing code quality, dependency currency, RAI implementation, or factory/registry usage.
applyTo: "**"
---

# MAIVE QA — encoded rules

> Mirror of [docs/qa/qa-checklist.md](../../docs/qa/qa-checklist.md). The
> canonical script is [`qa_audit.py`](../../src/backend/app/cli/qa_audit.py).

## How to use these rules
- For any change touching `src/backend/` or `src/frontend/`, an agent SHOULD run
  `uv run python -m app.cli.qa_audit all` from `src/backend/` before declaring
  the work complete.
- For ad-hoc reviews (no script run), use the grep patterns below.

## Rubric 1 — Clean & modular
- `rg -n "from app\.infrastructure" src/backend/app/domain` → must be empty.
- `rg -n "from app\.infrastructure\.persistence" src/backend/app/api` → must be empty.
- `rg -n "from app\.infrastructure" src/backend/app/application` → must be empty.
- Entities (`src/backend/app/domain/entities/*.py`) must not import `httpx`,
  `requests`, `azure.cosmos`, or perform I/O at import time.

## Rubric 2 — Dynamic & extensible
- `rg -n "provider\s*==\s*[\"']" src/backend/app` → only allowed inside
  `**/registry.py`.
- `rg -n "if settings\." src/backend/app` → only allowed in
  `app/dependencies.py` and `**/registry.py`.

## Rubric 3 — Latest libraries
- `rg -n "from pydantic import BaseSettings" src/backend` → must be empty
  (use `pydantic-settings`).
- `rg -n "datetime\.utcnow\(" src/backend` → must be empty
  (use `datetime.now(UTC)`).
- `npx tsc -b` (in `src/frontend`) → exit 0.
- `uv run ruff check .` (in `src/backend`) → exit 0.

## Rubric 4 — RAI implemented (DEC-012 / DEC-013 / DEC-019)
- [`docs/rai-policy.md`](../../docs/rai-policy.md) exists.
- [`docs/threat-model.md`](../../docs/threat-model.md) exists.
- [`plan/architecture.md`](../../plan/architecture.md) mentions `bot_audit`.
- All 6 guardrail modules + `errors.py` exist under
  [`src/backend/app/infrastructure/rai/`](../../src/backend/app/infrastructure/rai/):
  `input_validator.py`, `topic_gate.py`, `prompt_injection.py`,
  `system_prompt.py`, `output_validator.py`, `audit.py`, `errors.py`.
- [`BotPipelineUseCase`](../../src/backend/app/application/use_cases/bot_pipeline_use_case.py)
  present and referenced from
  [`bot.py`](../../src/backend/app/api/routes/bot.py) (AI path).
- `bot.py` AI path does NOT call `CoordinationAgent.evaluate_session`
  directly — it MUST go through the pipeline.
- `bot_audit` container declared in
  [`infra/modules/cosmos.bicep`](../../infra/modules/cosmos.bicep) with
  partition key `/session_id`.
- `rg -n "except Exception" src/backend/app` → only allowed in audit-write
  blocks of `bot_pipeline_use_case.py` and `routes/bot.py` (DEC-019:
  audit must never break the request).
- `tests/rai/` suite present and green:
  `cd src/backend && uv run pytest tests/rai/ -v` → 42+ passing.
- Bot pipeline modules (when implemented) include: input validation, topic
  gate, prompt-injection check, system prompt, output validator, audit row.

## Rubric 5 — Factory / registry
- `src/backend/app/dependencies.py` builds the LLM provider via
  `LLMProviderRegistry.build(...)` (Phase P1).
- Agents built via `AgentRegistry.build(...)` (Phase P2).
- Cosmos repos built via `CosmosRepoRegistry.build(...)` (Phase P3).
- No `elif.*provider` branches anywhere in `src/backend/app`.

## Frontend cross-cutting
- All HTTP calls go through `src/frontend/src/api/client.ts`. No hardcoded URLs
  elsewhere: `rg -n "https?://" src/frontend/src --glob '!**/api/client.ts'`
  must be empty (except inside string literals in tests/comments).
- All user-facing strings flow through `useTranslation()` (no raw English/Spanish
  literals in TSX `>...<` text nodes).

## Documentation discipline
- Modified backend files SHOULD carry `# Documented in: docs/paper/...` near the top.
- Architectural changes get a `DEC-NNN` entry in [docs/decisions.md](../../docs/decisions.md)
  (only the user adds these; agents never invent them).
- Meaningful merges add a one-line entry to [docs/status.md](../../docs/status.md)
  under "What changed this week".

## Hard prohibitions for any agent applying these rules
- Do NOT edit `src/backend/app/domain/entities/`, `docs/decisions.md`,
  `docs/plan.md`, `docs/paper/`, or `tests/`.
- Do NOT auto-add DEC-NNN entries.
- Do NOT run write commands (`git push`, `azd up`, etc.) under the QA workflow.
