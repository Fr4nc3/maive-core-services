# MAIVE — Copilot dispatcher

> Auto-loaded into every Copilot chat in this workspace. Keep ≤2 KB.
> Detailed project rules live in [AGENTS.md](../AGENTS.md). Detailed
> per-area rules live in [.github/instructions/](instructions/).

## Always read first
[AGENTS.md](../AGENTS.md) → [docs/status.md](../docs/status.md) → [docs/decisions.md](../docs/decisions.md) (top 3 entries).

## Sub-agent delegation map

| If the user is asking about… | Delegate to |
|---|---|
| Code quality, lint, library currency, RAI rubric scan | `@maive-qa` |
| RAI guardrails, bot pipeline, prompt injection, audit rows, `bot.py`, `infrastructure/rai/` | `@maive-rai` |
| Deploy, `azd`, Bicep, Docker, Container Apps, App Service, Key Vault, RBAC, MI | `@maive-deploy` |
| Frontend, React, TSX, i18n, Vite, nginx config, `api/client.ts` | `@maive-frontend` |
| Unity serious game, `src/unity`, Spatial.io closing/sunset, migration off Spatial.io, single-player Unity, character controller, SDK selection, `MaiveClient.cs`, Unity telemetry | `@maive-unity` |
| Research methodology, RQ1/RQ2/RQ3, hypotheses, ARCS, concept inventory, stats | `@maive-research` |
| Cross-cutting feature planning, phase mapping, paper updates | `@maive-lead` |

If the user did not pick an agent, the default agent should answer but
**MUST** route to the right sub-agent if the request fits one of the
rows above.

## Hard rules (apply to every agent)

1. **Clean Architecture** — Domain → Application → Infrastructure → API.
   Inner layers never import outer layers.
2. **Unified bot endpoint** — every VR/web client hits `POST /api/bot/ask`
   with the same payload. Never create client-specific endpoints.
3. **No PII** — users identified by `(platform, platform_user_id)` +
   internal UUID. Optional `display_name` only. No email, no real name.
4. **No hard-coded provider switches** — use registries
   (`LLMProviderRegistry`, future `AgentRegistry`, `CosmosRepoRegistry`).
   No `if provider == "..."` outside `**/registry.py`.
5. **Every architectural change** appends a `DEC-NNN` entry to
   [docs/decisions.md](../docs/decisions.md), updates
   [docs/status.md](../docs/status.md) "What changed this week", and adds
   a paragraph to [docs/paper/maive-systems-engineering-extended.md](../docs/paper/maive-systems-engineering-extended.md).
6. **Never edit** `src/backend/app/domain/entities/`,
   [docs/decisions.md](../docs/decisions.md), [docs/plan.md](../docs/plan.md),
   `docs/paper/`, or `tests/` without explicit user instruction.
7. **Pre-PR gate** — `cd src/backend && uv run ruff check .` exits 0
   before declaring backend work complete.
8. **No secrets in env vars** — all secrets via Key Vault + system-assigned
   managed identity (DEC-018). Never `az ... --query keys`.
9. **RAI on `/api/bot/ask`** — every AI-path call must traverse
   the 6-stage pipeline (DEC-012/013/019) and write a `bot_audit` row.
10. **No Azure service keys** — never add API keys, tokens, credentials, or Azure
   service key fields to code/config. No `cosmos_key`, `azure_openai_key`,
   `COSMOS_KEY`, or `AZURE_OPENAI_KEY`. Use `Settings`
   (`src/backend/app/config.py`) for non-secret configuration and Azure
   credentials/RBAC for Cosmos DB and Azure AI Foundry auth.

## Out of scope (decline politely)
Production deployment automation against the *real* subscription, Entra ID
auth, mobile-native VR clients, Azure Front Door / WAF, multi-region.
