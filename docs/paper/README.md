# MAIVE — Systems-Engineering Paper Workflow

This folder holds the long-form internal **extended paper** and the future **publishable derivative** for the MAIVE thesis.

## Files

| File | Purpose | Edit when |
|---|---|---|
| [maive-systems-engineering-extended.md](maive-systems-engineering-extended.md) | Internal extended SE paper. **No length limit.** Captures every architectural detail — V-Model, multi-agent system, LLM abstraction, RAG, multi-platform clients, telemetry, RQ1/RQ2/RQ3 evaluation plan, even failed paths (e.g., DEC-008 Spatial.io API limitation). | Whenever a phase ships — add at least one paragraph cross-referencing the implementing files. |
| [maive-systems-engineering-publishable.md](maive-systems-engineering-publishable.md) | Publishable 8–12-page derivative built **after** the extended paper stabilises and after data collection completes (per thesis timeline: Aug 2026). Targets INCOSE / IEEE Transactions on Learning Technologies / IJSE Part B. | Only after extended paper sections are mature **and** real user-study data is available. |
| `figures/` | Mermaid sources for canonical diagrams (V-Model, multi-agent flow, DFD, identity model, deployment topology). One source per figure — used by both papers and the thesis. | Whenever architecture changes meaningfully. |
| `references.bib` | BibTeX entries seeded from the thesis references. | Add new citations as encountered. |

## Editing the extended paper (F4)

When a phase or feature ships:

1. Open the matching section (e.g., new identity endpoint → "Multi-Platform Client Strategy").
2. Add a paragraph describing what was built, citing the implementing files (use repo-relative markdown links).
3. If new design decision: append a `DEC-NNN` entry to [../decisions.md](../decisions.md) and link it from the paper section.
4. If a new diagram is needed: create the Mermaid source in `figures/` and reference it from the paper.
5. In the source file (entity/route/etc.), add a comment near the top:
   ```python
   # Documented in: docs/paper/maive-systems-engineering-extended.md#<section-anchor>
   ```

## Promoting to the publishable paper (F5)

The publishable paper is **not** edited until:

- ✅ Data collection completes (per thesis timeline: ~August 2026)
- ✅ The extended paper sections relevant to the contribution are mature
- ✅ Statistical analysis for RQ1/RQ2/RQ3 has produced real effect sizes (not the *expected* values currently in the thesis design)

Promotion process:

1. Choose a focused contribution (current candidate: *"Multi-Agent Adaptive VR for Astronomy Education with LLM Provider Abstraction — A Systems-Engineering Approach"*).
2. Distill the relevant extended-paper sections into the publishable template (8–12 pages, IEEE/ACM format).
3. Replace expected effect sizes with observed values.
4. Trim diagrams to the most informative subset (typically 4–6 figures).
5. Cross-link both papers — the publishable version must cite the extended internal report as a technical reference.

## Authoritative source for research design

All hypotheses, statistical thresholds, and expected effect sizes come from the thesis document at [../PhD-Astronomy World - Work In progress- francia-riesco.md](../PhD-Astronomy%20World%20-%20Work%20In%20progress-%20francia-riesco.md). Do not invent or modify them in either paper.

Decision rules already locked in the thesis:

| Topic | Threshold |
|---|---|
| Significance | p < 0.05 |
| Power | ≥ 0.80 |
| RQ1 expected effect | d ≈ 0.4–0.6 |
| RQ2 expected effect (self-report) | d ≈ 0.6–0.7 |
| RQ2 expected effect (telemetry) | d ≈ 0.5–0.6 |
| RQ2 telemetry → ARCS correlation | r ≥ 0.30 |
| RQ2 ARCS reliability | Cronbach α ≥ 0.80 |
| RQ3 expected effect (performance) | d ≈ 0.45–0.60 |
| RQ3 expected effect (transfer) | d ≈ 0.40–0.55 |
| RQ3 classifier validity | AUC ≥ 0.70 |
| RQ3 telemetry → outcome correlation | r ≥ 0.30 |
| Confidence intervals | 95% CI |

## Diagram conventions

- Use Mermaid in markdown blocks. The MAIVE Lead agent renders them via the `renderMermaidDiagram` tool when needed.
- One canonical figure per system aspect — both papers and the thesis chapters pull from the same source.
- Each figure includes a caption with a stable anchor (`<a id="fig-vmodel"></a>`) so other documents can deep-link.

## Citation management

- BibTeX file: [references.bib](references.bib) — seeded from the thesis reference list.
- Citation key format: `LastnameYear` (e.g., `Kersting2024`, `Bohne2021`).
- Always cite published peer-reviewed work for empirical claims; cite this repo's own `DEC-NNN` entries for design decisions.
