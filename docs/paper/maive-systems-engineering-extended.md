# MAIVE — A Multi-Agent Adaptive VR Platform for Astronomy Education with LLM Provider Abstraction

**Status:** Living internal extended paper. **No length limit.** Sections fill in as implementation phases ship.
**Last updated:** 2026-04-28
**Authoritative source for research design:** [../PhD-Astronomy World - Work In progress- francia-riesco.md](../PhD-Astronomy%20World%20-%20Work%20In%20progress-%20francia-riesco.md)
**Companion files:** [../decisions.md](../decisions.md) · [../plan.md](../plan.md) · [../status.md](../status.md) · [README.md](README.md)

---

## Abstract

> *To be drafted as the system stabilises. The publishable derivative will distill this section into 200–250 words.*

MAIVE (Mentor-Agent Immersive VR for Education) is a multi-agent AI-driven adaptive virtual reality platform for astronomy education. The system delivers immersive learning experiences across four heterogeneous client platforms (Spatial.io, VRChat, Unity single-player, and a flat web client) backed by a single FastAPI service implementing Clean Architecture over Azure Cosmos DB. Adaptive feedback is provided by four coordinated AI agents (User Modeling, Content Curation, Assessment, Coordination) operating against a vendor-agnostic LLM provider interface that switches between local Ollama and Azure AI Foundry by configuration alone. Static content for the non-adaptive control condition is served from the same unified bot endpoint, allowing identical client payloads across both experimental conditions. This paper documents the systems-engineering approach (V-Model traceability), architectural decisions, multi-platform integration strategy, RAG ingestion pipeline, and evaluation plan tied to three pre-registered research questions covering conceptual learning gains, engagement, and problem-solving transfer.

## 1. Introduction

> *Stub.* Frame the gap (no adaptive AI in astronomy VR per Marougkas 2024 review of 69 studies), the opportunity (multi-agent + LLM-RAG inside immersive 3D), and the contribution (a reusable multi-platform systems-engineering framework + open artifacts).

## 2. Related Work

> *Stub.* Cite VR-in-astronomy meta-analyses (Radianti 2020, Kersting 2024, Cecotti 2022); adaptive VR effects (Shirazi 2023, Mdaghri-Alaoui 2023); multi-agent in education (Wan 2024); LLM tutors (Dong 2024); ARCS engagement (Keller 2010).

## 3. Requirements & V-Model Traceability

> *Stub.* Reproduce the thesis V-Model (Figure 1 in the thesis) as Mermaid in `figures/vmodel.md`. Map each research contribution CR1–CR6 to its verification gate.

### 3.1 Research questions

- **RQ1** — Does multi-agent adaptive VR improve astronomy concept-inventory gains vs. non-adaptive VR?
- **RQ2** — Does real-time adaptive feedback raise ARCS engagement and behavioural telemetry indicators?
- **RQ3** — Does adaptive coaching improve problem-solving and conceptual transfer?

### 3.2 Statistical decision rules (locked in the thesis)

| Test | Threshold |
|---|---|
| Significance | p < 0.05 |
| Power | ≥ 0.80 |
| RQ1 expected effect | d ≈ 0.4–0.6 |
| RQ2 ARCS effect | d ≈ 0.6–0.7 |
| RQ2 telemetry → ARCS r | ≥ 0.30 |
| RQ2 reliability | Cronbach α ≥ 0.80 |
| RQ3 performance effect | d ≈ 0.45–0.60 |
| RQ3 transfer effect | d ≈ 0.40–0.55 |
| RQ3 classifier validity | AUC ≥ 0.70 |
| Reporting | 95% CI |

## 4. System Architecture

### 4.1 Clean Architecture layering

> *Stub.* Reference [../../plan/architecture.md](../../plan/architecture.md). Show the `Domain → Application → Infrastructure → API` rule and the dependency-inversion enforcement via `BaseCosmosRepository` (DEC-001).

### 4.2 Cosmos DB design

> *Stub.* List 11 containers and partition keys from [../../plan/architecture.md](../../plan/architecture.md). Reference DEC-001 (Clean Architecture + Cosmos DB).

### 4.3 Component diagram

> *Figure to add:* `figures/components.md` — presentation, API, application, domain, infrastructure, AI, analytics layers.

## 5. Multi-Agent AI System

> *Reference DEC-005.* Describe the four agents:
>
> - **User Modeling Agent** — telemetry → engagement metrics + knowledge gaps
> - **Content Curation Agent** — RAG vector search → NASA-sourced help text
> - **Assessment Agent** — Zone of Proximal Development → difficulty recommendation
> - **Coordination Agent** — orchestrator; produces final action; persists `AgentAction`
>
> Implementing files: `src/backend/app/infrastructure/agents/*_agent.py`, prompts in `src/backend/app/infrastructure/agents/prompts/*.txt`.
>
> Add diagram: `figures/multi-agent-flow.md`.

## 6. LLM Provider Abstraction

> *Reference DEC-004.* Document the `LLMProvider` ABC, `OllamaProvider`, `AzureFoundryProvider`, and the `LLM_PROVIDER` env switch. Cite implementing files:
>
> - [../../src/backend/app/infrastructure/ai/llm_provider.py](../../src/backend/app/infrastructure/ai/llm_provider.py)
> - [../../src/backend/app/infrastructure/ai/ollama_provider.py](../../src/backend/app/infrastructure/ai/ollama_provider.py)
> - [../../src/backend/app/infrastructure/ai/azure_foundry_provider.py](../../src/backend/app/infrastructure/ai/azure_foundry_provider.py)

## 7. RAG Pipeline

> *Reference DEC-003.* Document Cosmos DB DiskANN vector search, ingestion (markdown → section parsing → 512-word chunks with 64-overlap → batch embedding → store), and how the Content Curation Agent queries at runtime.
>
> Implementing files:
> - [../../src/backend/app/infrastructure/ai/knowledge_ingestion.py](../../src/backend/app/infrastructure/ai/knowledge_ingestion.py)
> - [../../src/backend/app/cli/ingest_knowledge.py](../../src/backend/app/cli/ingest_knowledge.py)

## 8. Multi-Platform Client Strategy

> *Reference DEC-006 (unified bot), DEC-007 (platform identifiers), DEC-008 (Spatial.io research-blocked), DEC-009 (unified identity).*

### 8.1 Identity model

`(platform, platform_user_id)` natural key + internal UUID. Endpoint: `POST /api/students/identify`. No PII.

### 8.2 Unified bot endpoint

`POST /api/bot/ask` — same payload for every client. Backend routes by `session.condition`.

### 8.3 Per-platform notes

| Platform | Approach | DEC |
|---|---|---|
| Web (flat) | Reference implementation; `platform = "web"` | — |
| Unity single-player | Thin `MaiveClient.cs` adapter; `platform = "unity"` | — |
| Spatial.io | Embedded web view (no server-callable API) | DEC-008 |
| VRChat | UDON `VRCStringDownloader` (GET-only); web-view bridge for POST | — |
| Sine Space | Future cross-platform option | — |

## 9. Telemetry & Adaptive Bot

> *Reference [../../plan/telemetry-model.md](../../plan/telemetry-model.md).* Document the 22 event types and the per-event-type payload schemas. Show how telemetry feeds the User Modeling Agent and the RQ3 classifier pipeline.

## 10. Static Bot for Control Condition

> *Reference DEC-002.* Document `help_content` Cosmos container schema, `GET /api/help` and the `seed_help_content.py` CLI (Phase D1).

## 11. Evaluation Plan

> *Stub — pre-registered design.* Re-state RQ1/RQ2/RQ3 hypotheses, the statistical decision rules from §3.2, and the data-collection timeline (Sep 2025 – Jul 2026 per the thesis).

## 12. Discussion

> *To be written post-implementation.* Tradeoffs of the unified-bot approach; cost of LLM provider abstraction; lessons from Spatial.io API limitation; generalisability of the systems-engineering approach to other STEM VR domains.

## 13. Future Work

> *Stub.* Auth (Entra ID), production deployment automation, mobile-native VR, additional LLM providers, fine-tuned NASA-content models, multi-user collaborative VR scenarios.

## 14. Conclusion

> *To be written when the system stabilises.*

## References

> *Maintained in BibTeX:* [references.bib](references.bib). Seed from the thesis reference list as paper sections fill in.

## Appendix A — Decision log

See [../decisions.md](../decisions.md) — DEC-001 through DEC-010 (current).

## Appendix B — Implementing files index

> *To be expanded.* For each section above, list the source files that implement it. Mirrors the cross-link discipline (Phase F8) — every meaningful backend file should carry a `# Documented in: docs/paper/maive-systems-engineering-extended.md#section` comment near the top.
