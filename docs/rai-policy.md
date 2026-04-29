# MAIVE — RAI Policy

> Authoritative reference for the Responsible-AI behaviour of `/api/bot/ask`.
> See DEC-012 (RAI baseline), DEC-013 (audit immutability), DEC-019 (pipeline).

## Scope
This policy applies to **every** call to `POST /api/bot/ask`, regardless of
session `condition` (`maive` AI path or `non-adaptive-vr` static path).

## Pipeline

```
input_validator → topic_gate → prompt_injection → system_prompt
  → CoordinationAgent.evaluate_session → output_validator → audit
```

Stages run in fixed order. Any short-circuit raises `BotPipelineError(stage, reason)`.
The audit row is **always** written before the request returns or re-raises
(the audit step is in a `finally` block).

### Stage 1 — `input_validator`
- Source: [`src/backend/app/infrastructure/rai/input_validator.py`](../src/backend/app/infrastructure/rai/input_validator.py)
- Length cap: ≤ 2000 characters
- Unicode normalisation: NFC
- Strip control chars (keep `\t \n \r`)
- Language whitelist: `{"en", "es"}`
- Failure → HTTP 422 `input_invalid` / `language_not_allowed` / `query_too_long` / `empty_query`

### Stage 2 — `topic_gate`
- Source: [`topic_gate.py`](../src/backend/app/infrastructure/rai/topic_gate.py)
- Lexical baseline against curated astronomy/planetary-science seed terms
  (en + es)
- Threshold `MIN_SCORE = 0.05` (≥ 1 hit in short queries)
- Future upgrade: embedding-distance variant (kept behind same `score()` signature)
- Failure → HTTP 422 `off_topic`

### Stage 3 — `prompt_injection`
- Source: [`prompt_injection.py`](../src/backend/app/infrastructure/rai/prompt_injection.py)
- Pattern + heuristic, weighted score → block at `≥ 0.5`
- Pattern corpus inspired by public Lakera PINT and NVIDIA garak corpora.
  We do not redistribute the corpora; the test fixtures are a small
  representative subset
- Failure → HTTP 403 `blocked` (no leakage of which pattern matched)

### Stage 4 — `system_prompt`
- Source: [`system_prompt.py`](../src/backend/app/infrastructure/rai/system_prompt.py)
- Versioned prompts loaded by `system_prompt_id`; one entry per
  `(version, language)`
- Audit row records the exact `system_prompt_id` used
- Current prompts: `astro-tutor-v1-en`, `astro-tutor-v1-es`

### Stage 5 — LLM call
- Sole LLM hop. Goes through the abstract `LLMProvider` (DEC-016 registry)
- Provider name + model name recorded in audit row

### Stage 6 — `output_validator`
- Source: [`output_validator.py`](../src/backend/app/infrastructure/rai/output_validator.py)
- Checks: PII echo (email, phone, IPv4), URL leak, instruction-leak
  patterns, and re-runs `topic_gate` on the output
- Failure → HTTP 502 `output_blocked` (the raw LLM output is **not** returned)

### Stage 7 — `audit`
- Source: [`audit.py`](../src/backend/app/infrastructure/rai/audit.py)
- Builds an immutable `BotAudit` row, persisted to Cosmos container
  `bot_audit` (partition key `/session_id`)
- See [`bot_audit` schema](#bot_audit) below

## `bot_audit`
Schema in [`src/backend/app/domain/entities/bot_audit.py`](../src/backend/app/domain/entities/bot_audit.py).

Key invariants:
- **Append-only.** No `update` / no `delete` on the repository interface
- **No raw text.** `query_hash` is sha256; raw query never stored. LLM output
  never stored
- **No PII.** Only `(platform, platform_user_id, internal UUID)` references;
  no email / real name / IP
- **Always written.** Both success and short-circuit paths emit one row
- **Both conditions.** Static (control) path also writes a `bot_path="static"`
  row so we can compare conditions

## Pipeline errors
Source: [`errors.py`](../src/backend/app/infrastructure/rai/errors.py).
`BotPipelineError(stage, reason, http_status, public_detail)` — `reason`
is for the audit row, `public_detail` is what the client sees.

## HTTP status map
| Failed stage | Status | Public detail |
|---|---|---|
| `input_validator` | 422 | `input_invalid` / `language_not_allowed` / `query_too_long` / `empty_query` |
| `topic_gate` | 422 | `off_topic` |
| `prompt_injection` | 403 | `blocked` |
| `output_validator` | 502 | `output_blocked` |
| LLM/network | 503 | `upstream_unavailable` |
| Success | 200 | normal `BotAskResponse` |

## Logging discipline
- Raw user query: **never logged**, **never persisted**. Only `sha256` hash
- Raw LLM output: **never logged**, **never persisted**. Block reasons only
- IP addresses: **never logged in audit**. (Edge Protector logs IPs at the
  network boundary only — DEC-017)
- Errors logged from RAI modules carry only `(stage, reason)` — no payload

## Retention
- `bot_audit` rows kept for the thesis duration + 1 year, then anonymised
  (drop `user_id`) per IRB protocol. (DEC-013)

## Out of scope (future phases)
- Real-time content safety service (Azure Content Safety)
- Adversarial red-team automation
- Per-session rate limiting
- Auth on `/api/bot/ask` (DEC-005 keeps this open; IRB-controlled access for now)
