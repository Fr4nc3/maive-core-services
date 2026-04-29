---
description: "MAIVE RAI guardrail rules. Apply to every file under src/backend/app/infrastructure/rai/ and to bot.py. Enforces the 6-stage pipeline, audit-row schema, no-raw-text-logging rule, and HTTP status map per DEC-012/013/019."
applyTo: "src/backend/app/infrastructure/rai/**,src/backend/app/api/routes/bot.py,src/backend/app/application/use_cases/bot_pipeline_use_case.py,src/backend/tests/rai/**"
---

# RAI guardrail rules — encoded

## The pipeline (order matters)
```
input_validator → topic_gate → prompt_injection → system_prompt
  → CoordinationAgent.evaluate_session → output_validator → audit
```

## Required modules under `src/backend/app/infrastructure/rai/`
- `input_validator.py` — length cap (≤2000 chars), Unicode NFC, strip
  control chars, language whitelist `{"en","es"}`.
- `topic_gate.py` — astronomy allowlist via embedding-distance against
  seed topics; threshold-based.
- `prompt_injection.py` — pattern + heuristic check (e.g.
  `ignore previous`, `system:`, role-confusion). Returns float score.
- `system_prompt.py` — versioned prompts loaded by `system_prompt_id`.
  One file per `(version, language)`; never inline prompt strings in
  agent code.
- `output_validator.py` — refuses PII echo, URL leak, instruction
  patterns; re-runs `topic_gate` on output.
- `audit.py` — pure helper; builds a `BotAudit` from intermediate results.
  No I/O.

## `BotAudit` row (immutable)
Required fields: `id`, `session_id`, `student_id`, `request_ts`,
`response_ts`, `query_hash` (sha256, **not raw text**), `query_length`,
`language`, `topic_gate_pass`, `prompt_injection_score`,
`system_prompt_id`, `output_validator_pass`, `output_validator_reasons`
(list[str]), `latency_ms`, `llm_provider`, `llm_model`, `error_code`
(nullable), `client_platform`, `client_version`. Partition key `/session_id`.

## Hard prohibitions (CI / qa_audit will enforce)
- `rg "user.*query|raw.*query|body\.query" src/backend/app/infrastructure/rai`
  → must NOT be followed by `logger.|print(|logging\.` for raw text.
- `rg "except Exception" src/backend/app/infrastructure/rai` → must be empty
  (use typed `BotPipelineError`).
- `rg "from openai|httpx" src/backend/app/infrastructure/rai/(input_validator|topic_gate|prompt_injection|output_validator|audit)\.py`
  → must be empty (only stage 5 calls the LLM).
- `bot.py` AI path must call `BotPipelineUseCase.execute(...)` — not
  `agent.evaluate_session(...)` directly.
- `infra/modules/cosmos.bicep` must contain a `bot_audit` container
  resource with partition key `/session_id`.

## HTTP status map (in `bot.py`)
| Failed stage | Status |
|---|---|
| input_validator | 422 |
| topic_gate | 422 |
| prompt_injection | 403 |
| output_validator | 502 |
| LLM/network | 503 |

## Test discipline
- One test file per stage under `src/backend/tests/rai/`.
- Prompt-injection tests cite their source corpus (Lakera/garak).
- Integration test (`test_bot_pipeline.py`) uses a `FakeLLMProvider`.
- `pytest src/backend/tests/rai/ -v` exits 0 in CI.

## Documentation discipline
- New RAI module → first non-import line is
  `# Documented in: docs/rai-policy.md#<section>`.
- Renaming/adding a stage → update Rubric 4 in
  [maive-qa.instructions.md](maive-qa.instructions.md) so
  `qa_audit rai-check` stays in sync.
- Behaviour-changing PR → append a `DEC-NNN` entry in
  [docs/decisions.md](../../docs/decisions.md).
