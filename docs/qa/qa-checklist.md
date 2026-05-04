# MAIVE QA Checklist

> Canonical pre-PR gate. Loaded by the `@maive-qa` agent and by
> [`maive-qa.instructions.md`](../../.github/instructions/maive-qa.instructions.md).
> Run via [`qa_audit.py`](../../src/backend/app/cli/qa_audit.py).

Related permanent review plan: [Backend Sample-Code Review Plan](backend-sample-code-review-plan.md).

## Modes
- **audit-only** (default) — read-only; reports findings.
- **suggest-diffs** — agent proposes patches; user approves each one.
- **auto-fix** — `qa_audit.py --fix` runs lint/format auto-fixers only.
  Never touches: `app/domain/entities/`, `docs/decisions.md`, `docs/plan.md`,
  `docs/paper/`, any `tests/` directory.

## Five rubrics

### 1. Clean & modular (Clean Architecture)
| Check | Command | Expected | Fix |
|---|---|---|---|
| Domain has zero infra imports | `rg -n "from app\.infrastructure" src/backend/app/domain` | no matches | move helper to infrastructure |
| Routes don't import repositories directly | `rg -n "from app\.infrastructure\.persistence" src/backend/app/api` | no matches | route → use case → repo |
| Use cases depend on interfaces, not implementations | `rg -n "from app\.infrastructure" src/backend/app/application` | no matches | inject via constructor |
| Entities are pure dataclasses / pydantic models | `rg -n "import (httpx\|requests\|cosmos)" src/backend/app/domain/entities` | no matches | move side effect out |

### 2. Dynamic & extensible
| Check | Command | Expected | Fix |
|---|---|---|---|
| No `provider == "..."` outside registries | `rg -n "provider\s*==\s*[\"']" src/backend/app --glob '!**/registry.py'` | no matches | move to registry (Phase P) |
| No `if settings.X == "..."` branching outside dependencies/registry | `rg -n "if settings\." src/backend/app --glob '!app/dependencies.py' --glob '!**/registry.py'` | no matches | route through registry |

### 3. Latest libraries
| Check | Command | Expected | Fix |
|---|---|---|---|
| No Pydantic v1 imports | `rg -n "from pydantic import BaseSettings" src/backend` | no matches | use `pydantic-settings` |
| No deprecated `datetime.utcnow` | `rg -n "datetime\.utcnow\(" src/backend` | no matches | `datetime.now(UTC)` |
| Backend deps not >1 minor behind | `uv pip list --outdated` | empty (or curated allowlist) | `uv lock --upgrade` |
| Frontend deps not >1 minor behind | `npm outdated` | empty | `npm update` |
| TypeScript strict compiles | `npx tsc -b` | exit 0 | fix types |

### 4. RAI implemented (DEC-012 / DEC-013)
| Check | Command | Expected | Fix |
|---|---|---|---|
| `docs/rai-policy.md` exists | `Test-Path docs/rai-policy.md` | True | author it |
| `docs/threat-model.md` exists | `Test-Path docs/threat-model.md` | True | author it |
| `bot_audit` container in plan/architecture.md | `rg -n "bot_audit" plan/architecture.md` | matches | document it |
| Guardrail modules present | `rg -l "guardrail\|topic_gate\|prompt_injection" src/backend/app/infrastructure/agents` | matches | implement |
| No bare `except Exception` | `rg -n "except Exception" src/backend/app` | no matches | catch specific |

### 5. Factory / registry instead of if/else
| Check | Command | Expected | Fix |
|---|---|---|---|
| LLM provider built via registry | `rg -n "LLMProviderRegistry" src/backend/app/dependencies.py` | matches | Phase P1 |
| Agents built via registry | `rg -n "AgentRegistry" src/backend/app/dependencies.py` | matches | Phase P2 |
| Repos built via registry | `rg -n "CosmosRepoRegistry" src/backend/app/dependencies.py` | matches | Phase P3 |
| No if/elif provider branches in dependencies.py | `rg -n "elif.*provider" src/backend/app/dependencies.py` | no matches | Phase P1 |

## Cross-cutting (frontend)
- All API calls go through `src/frontend/src/api/client.ts` — no hardcoded URLs.
  - `rg -n "https?://" src/frontend/src --glob '!**/api/client.ts'` should be empty.
- All user-facing strings come from i18n dictionaries (`useTranslation`).

## Documentation discipline
- Every modified backend file should carry `# Documented in: docs/paper/...` near the top.
- Every architectural choice gets a `DEC-NNN` row in [docs/decisions.md](../decisions.md).
- Weekly entry appended to [docs/status.md](../status.md) "What changed this week".

## Report format expected from `@maive-qa`
```
## QA Report — <date>
| Rubric | Pass | Fail | Notes |
|---|---|---|---|
| 1. Clean & modular | … | … | … |
| 2. Dynamic & extensible | … | … | … |
| 3. Latest libraries | … | … | … |
| 4. RAI implemented | … | … | … |
| 5. Factory / registry | … | … | … |

### Top 3 actionable items
1. …
2. …
3. …
```
