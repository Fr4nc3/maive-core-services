# MAIVE Plan History

> Append-only log of structural changes to [`plan.md`](plan.md).
> One row per restructure. Newest at top. Never edit prior rows.

A "restructure" means any of:
- Renaming, merging, splitting, or removing a phase
- Adding a new template or layout section
- Re-ordering phases
- Changing the meaning of a column (e.g. status icons)

Routine task additions and status flips are **not** restructures and do not
need a history entry — they go straight into `plan.md`.

| Date | Author | Change | Reason | Linked DECs |
|---|---|---|---|---|
| 2026-04-29 | @maive-lead | Adopted strict [`plan-template.md`](plan-template.md). Re-rendered active phases (R, W, S, P4, V) in [`plan.md`](plan.md) with `Pillar` / `Goal` / `Owner agent` / `Status` headers. Pre-template phases (A–F, G–L, N, O, P, Q) preserved verbatim under a `--- Pre-template phases ---` divider; will be migrated lazily as they get touched. Established this history log. | User request: "we need a strict plan structure design, and a status document; if we restructure the plan, we need to keep a track of it." | DEC-023 |

## Entry rules
- New rows go **at the top**.
- `Linked DECs` column is empty if the restructure is purely organisational.
- Author = the sub-agent (or person) that drove the change.
- A single row can summarise a same-day batch of restructure edits; do not
  log each file edit individually.
- Reverting a prior restructure adds a new row (do not strike-through old rows).
