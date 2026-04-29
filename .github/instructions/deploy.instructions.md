---
applyTo: "infra/**,**/Dockerfile,docker-compose.yml,.dockerignore,azure.yaml,**/*.bicep"
---

# Deployment instructions

Apply when editing any infra-as-code, container, or azd file.

## Hard rules
- **Secrets only via Key Vault + system-assigned MI** (DEC-018). Never
  inline secrets in Bicep parameters or env vars.
- **`bicep build` exits 0** before any commit touching `infra/`.
- **New Cosmos containers** declared in `infra/modules/cosmos.bicep`
  with explicit `partitionKey` and a comment explaining WHY (link to a
  DEC if applicable).
- **New role assignments** sit alongside the resource that grants the
  role; document the principal (which MI) in a comment.
- **No App Service Plans without a tier comment.** Cost discipline.
- **Multi-stage Dockerfiles only.** Final image must not contain build
  toolchain (`gcc`, `nodejs` for backend, etc.).
- **`docker-compose.yml`** is for local dev only — must not reference
  Azure-only services (Key Vault, Front Door).
- **`azd up` is human-only.** Agents may run `azd provision --preview`
  but never `azd up`/`azd deploy` without explicit user approval.

## Pre-PR gate
- `az bicep build --file infra/main.bicep` exits 0
- `docker build -t maive-backend:test src/backend/` succeeds
- New container resource has matching audit/seed plan in `docs/deployment/`
