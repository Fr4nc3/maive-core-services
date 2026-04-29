# Secrets & Configuration

> Companion to [runbook.md](runbook.md). Encodes the rule: **no secrets in the repo, no secrets in environment variables of cloud apps**.

## Where each piece lives

| Item | Location | Surfaced to backend as |
|---|---|---|
| Cosmos endpoint | Bicep output → Container App env | `COSMOS_ENDPOINT` |
| Cosmos auth | **Managed Identity** (no key) | (none — SDK uses MI) |
| Azure OpenAI endpoint | Bicep output → Container App env | `AZURE_OPENAI_ENDPOINT` |
| Azure OpenAI auth | **Managed Identity** (no key) | (none — SDK uses MI when key absent) |
| Chat / embedding deployment names | Bicep param → Container App env | `AZURE_OPENAI_CHAT_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` |
| App Insights connection string | Bicep output → Container App env | `APPLICATIONINSIGHTS_CONNECTION_STRING` |
| Key Vault name | Bicep output → Container App env | `KEY_VAULT_NAME` |
| Edge Protector token | **Local researcher laptop only** (never deployed) | n/a (sidecar reads `EDGE_PROTECTOR_TOKEN`) |
| Future: Entra app registration secret | Key Vault | (not yet — DEC-005 open) |

## GitHub Actions

| Use | Storage |
|---|---|
| `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_CLIENT_ID`, `AZURE_LOCATION` | Repository **vars** |
| Federated credential | Configured on the Entra app registration (no secret stored) |

## `.env` files

- `src/backend/.env` — local-dev only; **gitignored**.
- `src/edge-protector/.env` — local-dev only; **gitignored**.
- No `.env` is mounted into a deployed container; cloud config comes from
  Bicep + Key Vault references.

## Rotating

- **OpenAI / Cosmos keys** — not used (managed identity). Rotation is automatic.
- **Edge Protector token** — set a new value, restart the sidecar.
- **GitHub federated credential** — re-create the federated credential on the Entra app reg if compromised; no secret to rotate.
