# MAIVE Core Services — Architecture

## Overview

MAIVE (Multi-Agent Intelligent Virtual Environment) is an adaptive VR astronomy education platform.
This document defines the architecture for the **backend API** and **frontend dashboard**.

## Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Backend     | Python 3.12, FastAPI, UV                |
| Agent       | Agent Framework + LLM Provider abstraction |
| LLM (dev)   | Ollama (llama3 + nomic-embed-text)      |
| LLM (prod)  | Azure AI Foundry (OpenAI SDK)           |
| Database    | Azure Cosmos DB (NoSQL + DiskANN vector)|
| Frontend    | React 18 + TypeScript + Vite            |
| Cloud       | Azure (App Service, Functions, Monitor) |
| Auth        | Azure Entra ID (future)                 |

## Supported Platforms

| Value | Platform | Use Case |
|-------|----------|----------|
| `spatial.io` | Spatial.io | Primary immersive VR collaboration |
| `vrchat` | VRChat | Community VR social environment |
| `sinespace` | Sine Space | Cross-platform virtual world |
| `web` | Web (flat) | Browser-based 2D fallback |

## Clean Architecture (Backend)

```
┌─────────────────────────────────────────────────┐
│                   API Layer                     │
│         (FastAPI routes, middleware)             │
├─────────────────────────────────────────────────┤
│              Application Layer                  │
│        (Use cases, DTOs, interfaces)            │
├─────────────────────────────────────────────────┤
│               Domain Layer                      │
│   (Entities, value objects, repository ports)   │
├─────────────────────────────────────────────────┤
│            Infrastructure Layer                 │
│  (Cosmos DB repos, AI agents, LLM providers)    │
└─────────────────────────────────────────────────┘
```

### Dependency Rule
- Inner layers never depend on outer layers.
- Domain has zero external dependencies.
- Application depends only on Domain.
- Infrastructure implements Domain interfaces.
- API depends on Application (and injects Infrastructure).

## Domain Entities

| Entity               | Container              | Partition Key   | Description |
|----------------------|------------------------|-----------------|-------------|
| User              | `users`             | `/id`           | Learner profile, group assignment |
| Session              | `sessions`             | `/user_id`   | VR learning session with platform, condition, difficulty |
| Assessment           | `assessments`          | `/user_id`   | Pre/post test scores, normalized gain |
| TelemetryEvent       | `telemetry`            | `/session_id`   | VR behavioral data (22 event types) |
| AgentAction          | `agent_actions`        | `/session_id`   | AI agent decisions and scaffolding |
| TaskAttempt          | `task_attempts`        | `/session_id`   | Open-ended challenge attempts (RQ3) |
| ARCSSurveyResponse   | `arcs_surveys`         | `/session_id`   | ARCS motivational survey (RQ2) |
| QualitativeFeedback  | `qualitative_feedback` | `/session_id`   | Open-ended text reflections |
| ClassifierPrediction | `classifier_predictions`| `/session_id`  | ML predicted success probability |
| HelpContent          | `help_content`         | `/planet`       | Static bot responses (control group) |
| KnowledgeDocument    | `knowledge_documents`  | `/body_id`      | NASA RAG chunks with vector embeddings |
| BotAudit             | `bot_audit`            | `/session_id`   | Append-only RAI audit per `/api/bot/ask` (DEC-013/019) |

## Multi-Agent AI System

```
Unity (VR client)
    │
    ▼
POST /api/bot/ask  ←── unified endpoint, same request for both conditions
    │
    ├─ condition = "non-adaptive-vr" ──► Static HelpContent lookup
    │
    └─ condition = "maive" ──► Coordination Agent
                                    │
                        ┌───────────┼───────────┐
                        ▼           ▼           ▼
                  User Modeling  Assessment  Content Curation
                  (telemetry)   (ZPD/diff)  (RAG + NASA data)
```

### LLM Provider Abstraction

All agents use the `LLMProvider` interface (chat + embed). Switching is config-only:

- `LLM_PROVIDER=ollama` — local dev (httpx → Ollama REST API)
- `LLM_PROVIDER=azure` — production (openai SDK → Azure AI Foundry)

## API Endpoints

### Data Collection
| Method | Path                              | Description |
|--------|-----------------------------------|-------------|
| POST   | `/api/users`                   | Create user |
| GET    | `/api/users/{id}`              | Get user |
| GET    | `/api/users`                   | List users |
| POST   | `/api/sessions`                   | Start VR session |
| PATCH  | `/api/sessions/{id}`              | Update/end session |
| GET    | `/api/sessions/{id}`              | Get session details |
| POST   | `/api/assessments`                | Submit assessment |
| GET    | `/api/assessments/{id}`           | Get assessment results |
| POST   | `/api/telemetry`                  | Ingest telemetry event |
| GET    | `/api/telemetry/{session}`        | Get session telemetry |
| POST   | `/api/task-attempts`              | Record task attempt |
| POST   | `/api/arcs-surveys`               | Submit ARCS survey |
| POST   | `/api/qualitative-feedback`       | Submit qualitative feedback |
| POST   | `/api/classifier-predictions`     | Record classifier prediction |

### Bot & Agents
| Method | Path                              | Description |
|--------|-----------------------------------|-------------|
| POST   | `/api/bot/ask`                    | **Unified bot** — routes to static or AI based on condition |
| POST   | `/api/agents/adapt`               | Direct AI agent pipeline (debug/admin) |

### Static Help Content (admin)
| Method | Path                              | Description |
|--------|-----------------------------------|-------------|
| GET    | `/api/help?planet=mars&...`       | Query static help content |
| GET    | `/api/help/planets`               | List planets with content |
| POST   | `/api/help`                       | Create help content item |
| PATCH  | `/api/help/{planet}/{id}`         | Update help content item |

### System
| Method | Path                              | Description |
|--------|-----------------------------------|-------------|
| GET    | `/api/health`                     | Health check |

## Frontend Structure

Single-page React dashboard for researchers and instructors:
- User management
- Session monitoring
- Assessment results visualization
- Telemetry analytics
- Agent action logs
