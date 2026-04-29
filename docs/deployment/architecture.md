# MAIVE Cloud Deployment — Architecture

> Cloud topology for MAIVE Core Services. Local-only setup: see [RUNLOCAL.md](../RUNLOCAL.md).
> Decisions: [DEC-017](../decisions.md) (LLM split) · [DEC-018](../decisions.md) (topology).

## Topology diagram

```mermaid
flowchart LR
  subgraph Browser
    L[Learner browser]
  end
  subgraph Azure[Azure subscription · rg-maive-{env}]
    AS[App Service B1<br/>Linux container · nginx<br/>frontend]
    CA[Container App<br/>FastAPI backend<br/>system-assigned MI]
    ACR[(Azure Container<br/>Registry)]
    KV[(Key Vault<br/>RBAC mode)]
    COS[(Cosmos DB<br/>NoSQL · serverless<br/>DiskANN vector idx)]
    AIF[Azure AI Foundry<br/>chat + embedding<br/>deployments]
    LAW[(Log Analytics<br/>Workspace)]
    AI[(Application<br/>Insights)]
  end
  subgraph Researcher[Researcher laptop · optional]
    OLL[Ollama]
    EP[Edge Protector<br/>FastAPI sidecar]
    TUN((Cloudflare<br/>Tunnel))
  end

  L -->|HTTPS| AS
  AS -->|/api/* reverse proxy<br/>HTTPS| CA
  CA -->|MI| COS
  CA -->|MI| AIF
  CA -->|MI| KV
  CA -->|pulls image| ACR
  AS -.->|app insights SDK| AI
  CA -.->|app insights SDK| AI
  AI -->|workspace| LAW
  CA -. debug only .-> TUN
  TUN --> EP
  EP --> OLL
```

## Resource map

| Concern | Azure resource | Notes |
|---|---|---|
| Frontend hosting | App Service (B1, Linux container) | nginx alpine; reverse-proxies `/api/*` |
| Backend hosting | Container Apps Environment + 1 Container App | min/max replicas 1/3; system MI |
| Container images | Azure Container Registry (Basic) | `AcrPull` granted to backend MI |
| Persistence | Cosmos DB serverless (NoSQL) | DB `maive`; containers created on first use; vector search capability enabled |
| LLM | Azure AI Foundry (Azure OpenAI) | deployments: `chat` + `embedding` |
| Secrets | Key Vault (RBAC mode) | `Key Vault Secrets User` granted to backend MI |
| Telemetry | Application Insights (workspace-based) + Log Analytics | shared by frontend + backend |

## Identity flow

- Backend Container App has a **system-assigned managed identity**.
- That identity holds:
  - `AcrPull` on the registry → can pull its own image
  - `Cosmos DB Built-in Data Contributor` (data plane) → reads/writes containers
  - `Cognitive Services OpenAI User` on the AI Foundry account → invokes deployments
  - `Key Vault Secrets User` → reads secrets at runtime
- No connection strings or keys in env vars. Endpoints only.

## Network model (current)

Public ingress on both App Service and Container App. Cosmos / AI Foundry / Key
Vault are accessed over their public endpoints with RBAC. **Private networking
variant (VNet + private endpoints + WAF) is deferred** to thesis-defence cleanup
(`azure_custom.yaml` per MACAE pattern).

## Edge Protector (debug-only)

Researcher laptop runs [`src/edge-protector/`](../../src/edge-protector/) which
exposes a token-protected, IP-allowlisted FastAPI proxy in front of a local
Ollama. Exposed via Cloudflare Tunnel / dev tunnel for short-lived debug sessions
only. **Never used by experiment runtime.**
