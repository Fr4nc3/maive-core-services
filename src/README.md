# MAIVE Core Services

Adaptive VR Astronomy Education Platform — backend API and researcher dashboard.

## Quick Start

### Backend (Python 3.12 + FastAPI + UV)

```bash
cd src/backend

# Install UV if you don't have it
# pip install uv   OR   winget install astral-sh.uv

# Create venv and install dependencies
uv sync

# Run the dev server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be at **http://localhost:8000/docs** (Swagger).

### Frontend (React + Vite)

```bash
cd src/frontend
npm install
npm run dev
```

Dashboard at **http://localhost:5173**.

### Environment Variables

Copy the `.env.example` files and fill in your values:

```bash
cp src/backend/.env.example src/backend/.env
cp src/frontend/.env.example src/frontend/.env
```

For local development, the backend `.env` ships pre-configured for the Azure Cosmos DB Emulator.

## Architecture

See [plan/architecture.md](plan/architecture.md) for the full architecture reference.

```
src/backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # pydantic-settings from .env
│   ├── dependencies.py       # DI wiring
│   ├── domain/               # Entities & repository interfaces
│   │   ├── entities/
│   │   └── interfaces/
│   ├── application/          # Use cases & DTOs
│   │   ├── use_cases/
│   │   └── dtos/
│   ├── infrastructure/       # Cosmos DB repos, AI agent
│   │   ├── persistence/cosmos_db/
│   │   └── agents/
│   └── api/routes/           # FastAPI route handlers

src/frontend/
├── src/
│   ├── api/client.ts         # Typed API client
│   ├── components/           # Shared components
│   ├── pages/                # Route pages
│   └── styles/               # Global CSS
```
