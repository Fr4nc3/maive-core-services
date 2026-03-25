# MAIVE Core Services — Architecture

## Overview

MAIVE (Multi-Agent Intelligent Virtual Environment) is an adaptive VR astronomy education platform.
This document defines the architecture for the **backend API** and **frontend dashboard**.

## Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Backend     | Python 3.12, FastAPI, UV                |
| Agent       | Azure AI / Agent Framework              |
| Database    | Azure Cosmos DB (NoSQL)                 |
| Frontend    | React 18 + TypeScript + Vite            |
| Cloud       | Azure (App Service, Functions, Monitor) |
| Auth        | Azure Entra ID (future)                 |

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
│  (Cosmos DB repos, Azure services, AI agents)   │
└─────────────────────────────────────────────────┘
```

### Dependency Rule
- Inner layers never depend on outer layers.
- Domain has zero external dependencies.
- Application depends only on Domain.
- Infrastructure implements Domain interfaces.
- API depends on Application (and injects Infrastructure).

## Domain Entities

| Entity       | Description                                        |
|--------------|----------------------------------------------------|
| Student      | Learner profile, group assignment, demographics     |
| Session      | VR learning session with start/end, condition       |
| Assessment   | Pre/post test scores, normalized gain               |
| Telemetry    | VR behavioral data (time on task, hints, errors)    |
| AgentAction  | AI agent decisions (adaptations, scaffolding)       |

## API Endpoints

| Method | Path                         | Description                    |
|--------|------------------------------|--------------------------------|
| POST   | /api/students                | Create student                 |
| GET    | /api/students/{id}           | Get student                    |
| GET    | /api/students                | List students                  |
| POST   | /api/sessions                | Start VR session               |
| PATCH  | /api/sessions/{id}           | Update/end session             |
| GET    | /api/sessions/{id}           | Get session details            |
| POST   | /api/assessments             | Submit assessment              |
| GET    | /api/assessments/{id}        | Get assessment results         |
| POST   | /api/telemetry               | Ingest telemetry event         |
| GET    | /api/telemetry/{session}     | Get session telemetry          |
| POST   | /api/agents/adapt            | Request AI adaptation          |
| GET    | /api/agents/actions/{id}     | Get agent action log           |
| GET    | /api/health                  | Health check                   |

## Cosmos DB Design

- **Database**: `maive`
- **Containers**:
  - `students` — partition key: `/id`
  - `sessions` — partition key: `/student_id`
  - `assessments` — partition key: `/student_id`
  - `telemetry` — partition key: `/session_id`
  - `agent_actions` — partition key: `/session_id`

## Frontend Structure

Single-page React dashboard for researchers and instructors:
- Student management
- Session monitoring
- Assessment results visualization
- Telemetry analytics
- Agent action logs
