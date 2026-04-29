# MAIVE Plan Template

> Use this template for every new phase added to [`plan.md`](plan.md). Phases that
> do not match this shape MUST be rewritten before merge. The QA agent will lint
> phase headings via `qa_audit pillars-check` (Rubric 6).

## How to use
1. Copy the section template below to the **top** of [`plan.md`](plan.md)
   (newest phase first).
2. Fill every field. If a field is N/A, write `N/A — <reason>`.
3. If you change the structure of [`plan.md`](plan.md) itself (rename phases,
   merge them, drop a phase), append a row to [`plan-history.md`](plan-history.md)
   in the same commit.
4. Pillar value MUST be one of: `Stable Core` · `Scenario Pack` ·
   `Configuration Layer` · `Customization Layer` (per
   [`docs/pillars_dev.md`](pillars_dev.md)).

## Section template (copy-paste)

```markdown
## Phase <CODE> — <Short title> (<DEC-NNN if any>)

**Pillar:** <Stable Core | Scenario Pack | Configuration Layer | Customization Layer>
**Goal:** <One sentence: what changes when this phase ships>
**Owner agent:** <@maive-lead | @maive-rai | @maive-deploy | @maive-frontend | @maive-research | @maive-qa>
**Status:** <⏳ Active | ✅ Done (YYYY-MM-DD) | ⏸ Deferred | ❌ Cancelled>

| ID | Artifact | Status |
|---|---|---|
| **<CODE>1** | <relative link or path> | <✅/⏳/⏸> (date) |
| **<CODE>2** | … | … |

**Verification:**
- <command or check that proves the phase shipped>
- <…>

**Decisions referenced:** <DEC-NNN, DEC-MMM>

**Out of scope:** <bullet list of intentionally-deferred sub-tasks>
```

## Phase code rules
- Phase codes are short (1–2 letters) and unique. Reusing a retired phase
  code requires a `plan-history.md` entry and an explicit `(supersedes …)`
  note in the phase title.
- Phase ordering in `plan.md` is **newest at top** (mirrors `decisions.md`).
- Each phase's "Status" column row uses one of: `✅ Done (YYYY-MM-DD)` ·
  `⏳` · `⏸ Operator step` · `⏸ Deferred` · `❌ Cancelled`.

## Field reference

| Field | Required | Notes |
|---|---|---|
| Pillar | ✅ | One of the four CWYD pillars. |
| Goal | ✅ | Present-tense, one sentence, no jargon. |
| Owner agent | ✅ | The sub-agent that drives the phase. |
| Status | ✅ | Header status; per-task status lives in the table. |
| Tasks table | ✅ | At minimum one row. ID = `<CODE><n>`. |
| Verification | ✅ | At least one check (command, file existence, or test). |
| Decisions referenced | optional | Any DEC-NNN this phase consumes or produces. |
| Out of scope | optional | Useful for keeping scope creep visible. |

## Anti-patterns (will fail review)
- "TBD" status with no owner — fill the owner before merging.
- Pillar omitted — pick the closest match; ask `@maive-lead` if unsure.
- Verification = "manual review" — name a real check or a checklist link.
- Editing a `✅ Done` task without recording the change in
  [`plan-history.md`](plan-history.md).
