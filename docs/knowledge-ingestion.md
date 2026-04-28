# Knowledge Ingestion Workflow

This document describes how to populate the MAIVE backend with the two
content layers used by the bot:

1. **Static help content** (HelpContent container) — deterministic
   answers tied to a planet/section. Used by the static bot path
   (`condition = control`).
2. **NASA RAG knowledge** (KnowledgeDocument container) — semantically
   chunked documents with vector embeddings. Used by the AI multi-agent
   path (`condition = treatment`) for retrieval-augmented answers.

## Prerequisites

- Cosmos DB account reachable (env: `COSMOS_ENDPOINT`, `COSMOS_KEY`,
  `COSMOS_DATABASE`).
- One LLM provider configured:
  - **Ollama** (local dev): set `LLM_PROVIDER=ollama` and run
    `ollama pull nomic-embed-text` and your chat model
    (`OLLAMA_CHAT_MODEL`, `OLLAMA_EMBEDDING_MODEL`).
  - **Azure AI Foundry** (prod): set `LLM_PROVIDER=azure` and
    `AZURE_OPENAI_*` variables.

## 1. Seed static help content

Source layout:

```
data/help_content/
  mars/
    crater_lab.json
    intro.json
  jupiter/
    europa_orbit.json
```

Each JSON file contains a single `HelpContent` object or a list of
them. The folder name is used as the default `planet` if absent.

Run:

```powershell
cd src/backend
uv run python -m app.cli.seed_help_content
# or
uv run python -m app.cli.seed_help_content --planet mars
```

The CLI is **idempotent at the entity level**: each record is created
with a fresh UUID. To re-seed cleanly, drop the container or de-dup by
`(planet, content_topic, title)` upstream.

## 2. Ingest NASA knowledge for RAG

Source layout (markdown preferred):

```
data/nasa/
  mars/
    geology.md
    atmosphere.md
  jupiter/
    moons.md
```

Run:

```powershell
cd src/backend
uv run python -m app.cli.ingest_knowledge
uv run python -m app.cli.ingest_knowledge --provider azure
```

The ingestion pipeline:

1. Walks `data/nasa/<body>/*.md`.
2. Chunks each file (semantic / fixed-window — see
   `infrastructure/ai/knowledge_ingestion.py`).
3. Calls `EmbeddingService.embed_batch` via the configured provider.
4. Upserts each chunk into the `knowledge_documents` Cosmos container,
   partitioned by `body` (e.g. `mars`, `jupiter`).

Vector search uses Cosmos DB's DiskANN index (configured at container
provisioning time — see `infra/`).

## 3. Verify

After seeding, hit:

- `GET /api/health/cosmos` — confirms connectivity.
- `GET /api/help?planet=mars` — should list the seeded entries.
- `GET /api/health/llm` — confirms the embedding/chat provider responds.

## 4. Decisions

- **DEC-006**: Cosmos DB is the single store for both static help and
  vector knowledge.
- **DEC-007**: LLM provider is swappable via `LLM_PROVIDER` (ollama |
  azure) — no agent-side code change required.
- **DEC-008**: Static bot vs. AI bot is selected by
  `Session.condition`; the unified endpoint is `POST /api/bot/ask`.

See `docs/decisions.md` for the full log.
