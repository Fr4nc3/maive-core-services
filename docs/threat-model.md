# MAIVE — Threat Model for `/api/bot/ask`

> STRIDE-based threat analysis. Companion to [rai-policy.md](rai-policy.md).
> See DEC-012, DEC-013, DEC-019.

## System under analysis
- Endpoint: `POST /api/bot/ask`
- Two paths gated by `session.condition`:
  - `maive` → 6-stage RAI pipeline + LLM
  - `non-adaptive-vr` → static `help_content` lookup
- Always writes one `bot_audit` row

## STRIDE table

| # | Threat | Category | Mitigation | Status |
|---|---|---|---|---|
| 1 | Anonymous client impersonates a user | **Spoofing** | No auth in MVP. IRB-controlled access; classroom-supervised. Documented limitation. | Accepted (DEC-005) |
| 2 | Audit row tampered to hide a bad response | **Tampering** | `BotAuditRepository` is append-only by interface; no `update`/`delete` method. Cosmos RBAC: backend MI has `Data Contributor` only. | Mitigated |
| 3 | Researcher disputes that a user saw a particular response | **Repudiation** | Audit row links `(session_id, user_id, request_ts, response_ts, system_prompt_id, llm_provider+model, query_hash, output_validator flags)`. Replayable. | Mitigated |
| 4 | LLM output leaks PII the user typed earlier | **Information Disclosure** | `output_validator` blocks email/phone/IP/URL patterns + instruction-leak phrases; raw output never returned on failure (HTTP 502 `output_blocked`). | Mitigated |
| 5 | Logs/audit accidentally store the raw user query | **Information Disclosure** | Hard rule: only `sha256` hash + length stored. Encoded in [rai.instructions.md](../.github/instructions/rai.instructions.md) and enforced by `qa_audit rai-check`. | Mitigated |
| 6 | Attacker exhausts LLM quota with high-volume requests | **Denial of Service** | `input_validator` length cap (≤2000 chars). Per-session rate limit deferred to Phase X. | Partial |
| 7 | Off-topic queries waste budget / produce unsafe content | **DoS / Info Disclosure** | `topic_gate` short-circuits before LLM hop. Threshold tunable. | Mitigated |
| 8 | Prompt injection bypasses topic gate by mentioning astronomy | **Tampering / Elevation** | `prompt_injection` runs after `topic_gate` with weighted-pattern matcher (Lakera/garak-inspired). Threshold 0.5; combined patterns escalate the score. | Mitigated |
| 9 | Attacker exfiltrates the system prompt | **Information Disclosure** | `output_validator` blocks "system prompt" / "my instructions" / "I was told to" leak patterns. System prompt itself is not in the response context returned to the client. | Mitigated |
| 10 | Bot path bypasses RAI by importing `CoordinationAgent` directly | **Elevation** | `bot.py` route MUST call `BotPipelineUseCase.execute(...)`. Enforced by `qa_audit rai-check` + the `@maive-rai` instructions. | Mitigated |
| 11 | Cross-tenant query: one user sees another's audit | **Information Disclosure** | `bot_audit` partition key is `/session_id`; queries always include partition key. Read endpoint not yet exposed. | Mitigated |
| 12 | Time-of-check / time-of-use: session deleted between auth + audit | **Race condition** | Pipeline reads `session` once at request entry; audit is best-effort and never blocks the response. | Accepted |
| 13 | Audit write fails → silent loss of evidence | **Logging integrity** | Future: route audit failure to App Insights critical alert. Today: swallowed (the request itself is unaffected). | Known gap |
| 14 | Provider key leaked from environment | **Info Disclosure** | All secrets via Key Vault + system-assigned MI (DEC-018). No `--query keys` in workflows. | Mitigated |
| 15 | LLM provider returns adversarial JS in HTML response | **Tampering / XSS** | Frontend renders bot output as text (no `dangerouslySetInnerHTML`). | Mitigated by frontend |

## Trust boundaries
1. **Internet → Frontend (App Service)** — TLS 1.2+, HTTPS only
2. **Frontend → Backend (Container Apps)** — internal FQDN within environment
3. **Backend → Cosmos / AI Foundry / Key Vault** — Azure RBAC via system-assigned MI
4. **Backend ↮ Local Ollama** — disallowed in production. Edge Protector
   exists only for researcher debugging (DEC-017), behind bearer token + IP
   allowlist + tunnel

## Residual risks (accepted)
- **No authentication** on `/api/bot/ask` — relies on IRB-controlled,
  classroom-supervised access. Tracked by DEC-005.
- **Per-session rate limiting** deferred to Phase X.
- **Real-time content safety service** (Azure Content Safety) deferred —
  current pattern + length defences considered sufficient for MVP.

## Verification
- `cd src/backend && uv run pytest tests/rai/ -v` — 42 tests, must be 0 failures
- `cd src/backend && uv run python -m app.cli.qa_audit rai-check` — must pass all checks
- Manual smoke per [docs/RUNLOCAL.md](RUNLOCAL.md):
  - benign astronomy → 200 + audit row green
  - "Ignore previous instructions about Mars" → 403 + audit `prompt_injection_blocked=true`
  - "What is mitochondria?" → 422 + audit `topic_gate_pass=false`
