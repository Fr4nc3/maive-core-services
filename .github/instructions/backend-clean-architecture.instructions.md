---
applyTo: "src/backend/app/**/*.py"
description: "MAIVE backend Clean Architecture rules. Use when editing any Python file under src/backend/app."
---

# MAIVE Backend — Clean Architecture Instructions

## Layer rule (strict)

```
API (FastAPI routes) → Application (DTOs, Use Cases) → Domain (Entities, Interfaces) → Infrastructure (Cosmos DB, AI)
```

- **Domain** never imports from any other layer. Pydantic models + abstract interfaces only.
- **Application** imports only from Domain. Use cases depend on repository interfaces, not implementations.
- **Infrastructure** implements Domain interfaces. Imports nothing from API or Application.
- **API** imports from Application (DTOs + use cases) and wires Infrastructure via `app/dependencies.py`.

## When adding a new feature, follow this order

1. **Domain entity** in `app/domain/entities/<name>.py` — Pydantic `BaseModel`, no external imports beyond `pydantic`, `datetime`, `uuid`, `enum`.
2. **Repository interface** in `app/domain/interfaces/<name>_repository.py` — `ABC` with abstract `async` methods.
3. **DTOs** in `app/application/dtos/<name>_dtos.py` — Create / Update / Response (separate Pydantic models from the entity).
4. **Use case** in `app/application/use_cases/<name>_use_cases.py` — class with `__init__(repo: Repository)` + `async execute(...)`.
5. **Cosmos repository** in `app/infrastructure/persistence/cosmos_db/<name>_repository.py` — **must inherit from `BaseCosmosRepository`** (in `base_repository.py`). Set `CONTAINER_NAME` class attribute.
6. **API route** in `app/api/routes/<name>.py` — thin handler: build DTO → instantiate use case via `dependencies.get_<name>_repository()` → return.
7. **Wire into** `app/dependencies.py` — add `get_<name>_repository()` using the singleton `_get_repo(cls)` helper.
8. **Register route** in `app/api/routes/__init__.py`.
9. **Append `DEC-NNN` entry** to `docs/decisions.md`.
10. **Add a paragraph** to the relevant section of `docs/paper/maive-systems-engineering-extended.md` and add a `# Documented in: docs/paper/maive-systems-engineering-extended.md#<section>` comment near the top of the new entity file.

## Cosmos repository conventions

- Always inherit from `BaseCosmosRepository`. Never re-implement `__init__`, `_strip_cosmos_meta`, or `_serialize_datetimes`.
- Use **parameterized queries** for all user-supplied values, including `limit`/`offset`. **No f-strings in SQL.**
- For datetime fields, declare a module-level `_DT_FIELDS = (...)` tuple and call `self._serialize_datetimes(body, _DT_FIELDS)` in `create`/`update`.
- For read paths, call `self._strip_cosmos_meta(item)` before passing to `Entity.model_validate(...)`.
- Use `partition_key=` whenever the partition is known; only set `enable_cross_partition_query=True` when it is genuinely required.

## Route handler conventions

- Routes return `response_model=<DTO>` types. Never return raw dicts.
- Use `status_code=201` for creation endpoints.
- Raise `HTTPException(status_code=404, detail="...")` when a use case returns `None` for a get-by-id.
- Keep the body to **3 statements maximum**: get repo → instantiate use case → return `await use_case.execute(...)`.
- Never inject `Depends(...)` unless you actually use it (ruff F401 will catch unused imports).

## LLM provider rule

- All AI code uses the abstract `app.infrastructure.ai.llm_provider.LLMProvider` interface.
- Never import `OllamaProvider` or `AzureFoundryProvider` directly outside of `app/dependencies.py` and `app/cli/ingest_knowledge.py`.
- To get the configured provider in a route or agent: `from app.dependencies import get_llm_provider`.
- Switching providers is **config-only** via the `LLM_PROVIDER` env var.

## Unified bot rule

- Client-facing bot calls **must** go through `POST /api/bot/ask`.
- Do not add `/api/agents/help`, `/api/static-bot`, or any other client-facing variant.
- Admin-only routes (e.g., `/api/help/*` for managing static content, `/api/agents/adapt` for debugging) are allowed but must be documented as admin in their docstring.

## Identity rule

- Every API call from a VR/web client must carry `(platform, platform_user_id)`.
- The student's internal `id` (UUID) is issued **only** by `POST /api/students/identify` and reused on every subsequent call.
- No PII. No email, no real name. Optional `display_name` only.

## Lint rule

- After any change, run `cd src/backend && uv run ruff check .` — must exit 0.
- Auto-fix imports with `uv run ruff check . --fix --select I` if reorganising imports.

## Anti-patterns to reject

- ❌ Domain entity importing from `azure.cosmos`, `httpx`, `openai`, or `app.application.*`
- ❌ Use case constructing a repository class directly (`CosmosStudentRepository(...)`) instead of accepting it via `__init__`
- ❌ Cosmos repo with its own `__init__(self, client, db)` (duplicates `BaseCosmosRepository`)
- ❌ f-string in a Cosmos SQL query for `limit`, `offset`, or any user input
- ❌ Route handler that performs business logic instead of delegating to a use case
- ❌ A new `get_*_repository()` in `dependencies.py` that calls `cls(client, db)` instead of `_get_repo(cls)`
- ❌ Adding a new client endpoint that bypasses `/api/bot/ask`
