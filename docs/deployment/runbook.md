# MAIVE Cloud Deployment — Runbook

> Companion to [architecture.md](architecture.md), [DEC-018](../decisions.md),
> and [`azure.yaml`](../../azure.yaml).
> Local-only? See [docs/RUNLOCAL.md](../RUNLOCAL.md).

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Azure CLI | 2.65+ | `winget install Microsoft.AzureCLI` |
| Azure Developer CLI (`azd`) | 1.10+ | `winget install Microsoft.Azd` |
| Docker Desktop | 4.30+ | <https://www.docker.com/products/docker-desktop> |
| `bicep` | bundled with az | `az bicep install` |

You also need an Azure subscription where you can create resources and assign
roles (Owner OR Contributor + User Access Administrator).

## First-time provisioning

```pwsh
# 1. Login
az login --tenant <your-tenant-id>
azd auth login

# 2. Initialize a new azd environment
azd env new dev
azd env set AZURE_LOCATION eastus2
azd env set AZURE_SUBSCRIPTION_ID <sub-id>

# 3. Provision + deploy in one go
azd up
```

`azd up` runs:
1. **Provision** — `infra/main.bicep` against `rg-maive-<env>`.
2. **Build** — Docker images for backend + frontend.
3. **Deploy** — push to ACR, update Container App revision, push to App Service.
4. **Hooks** — `azure.yaml` `postprovision` prints the FQDNs.

## Update existing deployment

```pwsh
azd deploy             # code-only (no infra change)
azd provision          # infra-only
azd up                 # both
```

## Smoke test

```pwsh
$BACKEND = azd env get-values | Select-String '^BACKEND_URI=' | ForEach-Object { ($_ -split '=')[1].Trim('"') }
curl "$BACKEND/api/health"
```

Expected: `{"status":"ok","cosmos":{...},"llm":{...}}`.

## Tear down

```pwsh
azd down --purge --force
```
> `--purge` deletes soft-deleted Key Vault and AI Foundry resources too.

## CI/CD

- [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — runs on every PR/push.
- [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml) — manual (`workflow_dispatch`) `azd up` against the chosen environment, using federated GitHub OIDC.

GitHub repository **vars** required for `deploy.yml`:
- `AZURE_LOCATION`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID` (federated identity client id)

See [secrets.md](secrets.md) for the secret-vs-vars-vs-Key-Vault matrix.

## Common issues

| Symptom | Fix |
|---|---|
| `azd up` fails with `RoleAssignmentExists` | Pre-existing assignment with same GUID — safe to ignore on re-runs |
| Container App stuck on old image | `az containerapp revision restart -n <name> -g <rg>` |
| Cosmos vector index missing | First-run `seed_help_content` / `ingest_knowledge` creates containers; vector index is set in code at container creation time |
| Frontend `502` to `/api/*` | Check App Service `BACKEND_URL` setting points to the backend Container App FQDN with `https://` |
