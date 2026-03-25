# MAIVE Telemetry Model

## Overview

This document defines the telemetry data model for the MAIVE platform, derived from the three research questions in the PhD thesis. Every metric the system collects is mapped to the RQ that consumes it and to the analysis technique that processes it.

---

## 1. Research-Question → Telemetry Mapping

| RQ | What We Need | Telemetry Source |
|----|-------------|-----------------|
| **RQ1** – Learning outcomes | Pre/post concept-inventory scores, normalized gain | `Assessment` entity (existing) |
| **RQ1** – Agent effectiveness | Agent prompts delivered, learner responses to prompts | `AgentAction` (existing) + `TelemetryEvent` |
| **RQ2** – Engagement (ARCS) | Attention, Relevance, Confidence, Satisfaction scores | **`ARCSSurveyResponse`** (new) |
| **RQ2** – Behavioral engagement | Idle time, persistence (retries), hint rate, time-on-task | `TelemetryEvent` (expanded) |
| **RQ2** – Qualitative feedback | Open-ended text reflections | **`QualitativeFeedback`** (new) |
| **RQ3** – Problem-solving process | Time per step, hint frequency, error count, retries, trajectory revisions | `TelemetryEvent` + **`TaskAttempt`** (new) |
| **RQ3** – Classifier features | Aggregated behavioral features per session | Derived from `TelemetryEvent` at query time |
| **RQ3** – Transfer assessment | Follow-up rubric scores post-challenge | `Assessment` entity (type = `transfer`) |
| **RQ3** – Classifier predictions | Predicted success probability per session | **`ClassifierPrediction`** (new) |

---

## 2. Entity Catalog

### 2.1 Existing Entities (minor expansions)

#### Student
Identifies users only by `id` and `spatial_id` (Spatial.io identifier). No email or display name is collected.

#### Session
Add fields to support richer session context:

| Field | Type | Description |
|-------|------|-------------|
| `module_id` | `str` | Which VR module/scenario was active |
| `vr_device` | `str` | HMD type (Quest, PCVR, desktop) |
| `total_duration_ms` | `int | None` | Computed on session end |
| `total_hints_requested` | `int` | Running counter updated by event ingestion |
| `total_errors` | `int` | Running counter |
| `total_tasks_completed` | `int` | Running counter |

#### Assessment
Add `rater_scores` for inter-rater reliability on open-ended tasks:

| Field | Type | Description |
|-------|------|-------------|
| `rater_scores` | `list[dict]` | `[{rater_id, score, notes}]` for rubric-scored items |
| `rubric_threshold` | `float | None` | Success threshold (e.g. ≥ 8/10 → label 1) |

#### AgentAction
Add fields to track which agent type acted, bot type, and learning context:

| Field | Type | Description |
|-------|------|-------------|
| `agent_role` | `str` | `"conceptual"` or `"procedural"` (Mentor-Agent roles) |
| `bot_type` | `str` | `"hardcoded"` (static data bot) or `"ai"` (AI-optimized bot) |
| `task_id` | `str \| None` | Links to the task the student was on |
| `section` | `str` | Planet or area where the action occurred |
| `content` | `str` | Content topic the action relates to |
| `trigger_reason` | `str` | What behavioral threshold triggered this action |
| `student_response` | `str | None` | How the student reacted to the agent prompt |

---

### 2.2 Expanded Entity: TelemetryEvent

The `TelemetryEvent` is the **core data stream** from Unity. It captures events triggered by user interactions (primarily help requests) rather than continuous movement tracking. Each event records the **section** (planet/area), **content** topic, and — for help events — the **help text** and **bot type** used.

#### Event Types (enum)

```
# ── Help Interactions (primary telemetry) ──
HELP_REQUESTED           # User clicked for help
HELP_DELIVERED           # Bot delivered help response
HELP_DISMISSED           # User dismissed the help
HELP_FOLLOWED            # User acted on help suggestion

# ── Section Navigation ──
SECTION_ENTERED          # User entered a planet/section
SECTION_EXITED           # User left a planet/section

# ── Task Interaction ──
TASK_STARTED             # Student begins a task/challenge
TASK_STEP_COMPLETED      # Student completes one step within a task
TASK_COMPLETED           # Student finishes entire task
TASK_ABANDONED           # Student leaves task before completion

# ── Errors & Retries ──
ERROR_COMMITTED          # Student made an incorrect action
RETRY_ATTEMPTED          # Student retried after an error

# ── Assessment ──
QUIZ_ANSWER_SUBMITTED    # In-VR quiz answer recorded
SURVEY_COMPLETED         # ARCS survey completed (links to ARCSSurveyResponse)

# ── Agent Interaction ──
AGENT_PROMPT_DISPLAYED   # Agent showed a prompt to the student
AGENT_PROMPT_DISMISSED   # Student closed an agent prompt
AGENT_PROMPT_FOLLOWED    # Student acted on an agent prompt

# ── Session Lifecycle ──
SESSION_PAUSED           # Student paused VR session
SESSION_RESUMED          # Student resumed VR session
MODULE_ENTERED           # Student entered a new learning module
MODULE_EXITED            # Student exited a learning module

# ── Idle Detection ──
IDLE_DETECTED            # No user interaction for a threshold period (e.g. >60s)
```

#### TelemetryEvent Fields

Instead of `position` (x/y/z), each telemetry event carries contextual fields:

| Field | Type | Description |
|-------|------|-------------|
| `section` | `str` | Planet or area, e.g. `"mars"`, `"jupiter"`, `"solar-system"` |
| `content` | `str` | Content topic, e.g. `"orbital-mechanics"`, `"atmosphere"` |
| `help_text` | `str` | The help content shown to the user (for help events) |
| `bot_type` | `str` | `"hardcoded"` or `"ai"` — which bot provided the help |

#### Bot Types

Users are assigned one of two bot types:
- **`hardcoded`** — delivers pre-written, static help responses from a data file
- **`ai`** — uses an AI model to generate optimized, context-aware answers depending on the user's history and section

#### Payload Schemas by Event Type

| Event Type | Payload Fields |
|-----------|---------------|
| `HELP_REQUESTED` | `{task_id, step_index, context}` |
| `HELP_DELIVERED` | `{task_id, step_index, bot_type, help_text, agent_role}` |
| `HELP_DISMISSED` | `{help_id, time_visible_ms}` |
| `HELP_FOLLOWED` | `{help_id, follow_action, time_to_respond_ms}` |
| `SECTION_ENTERED` | `{section, section_name}` |
| `SECTION_EXITED` | `{section, time_in_section_ms}` |
| `TASK_STARTED` | `{task_id, task_name, task_type, difficulty_level}` |
| `TASK_STEP_COMPLETED` | `{task_id, step_index, step_name, time_on_step_ms, errors_in_step, hints_in_step}` |
| `TASK_COMPLETED` | `{task_id, total_time_ms, total_errors, total_hints, score, success}` |
| `TASK_ABANDONED` | `{task_id, last_step_index, time_spent_ms, reason}` |
| `ERROR_COMMITTED` | `{task_id, step_index, error_type, error_detail}` |
| `RETRY_ATTEMPTED` | `{task_id, step_index, retry_count, previous_error_type}` |
| `QUIZ_ANSWER_SUBMITTED` | `{question_id, answer, correct, time_to_answer_ms}` |
| `AGENT_PROMPT_DISPLAYED` | `{agent_action_id, agent_role, prompt_type}` |
| `AGENT_PROMPT_FOLLOWED` | `{agent_action_id, follow_action, time_to_respond_ms}` |
| `MODULE_ENTERED` | `{module_id, module_name}` |
| `MODULE_EXITED` | `{module_id, time_in_module_ms}` |
| `IDLE_DETECTED` | `{idle_duration_ms, last_action_type, task_id, section}` |
| `SURVEY_COMPLETED` | `{survey_type, survey_id, completion_time_ms}` |

---

### 2.3 New Entity: TaskAttempt

Tracks a student's full attempt at an open-ended challenge (RQ3). Aggregates step-level data from `TelemetryEvent` into a single record per attempt.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID |
| `session_id` | `str` | FK to Session |
| `student_id` | `str` | FK to Student |
| `task_id` | `str` | Identifier of the challenge template |
| `task_name` | `str` | Display name |
| `task_type` | `str` | `"orbital_trajectory"`, `"stellar_classification"`, `"gravitational_sim"` |
| `started_at` | `datetime` | |
| `completed_at` | `datetime | None` | |
| `status` | `str` | `"in_progress"`, `"completed"`, `"abandoned"` |
| `total_steps` | `int` | Number of steps in this task |
| `steps_completed` | `int` | Steps actually completed |
| `total_time_ms` | `int` | Wall-clock time on this attempt |
| `total_errors` | `int` | Error count |
| `total_retries` | `int` | Retry count |
| `total_hints_requested` | `int` | Hints the student asked for |
| `total_hints_delivered` | `int` | Hints the agent proactively gave |
| `trajectory_revisions` | `int` | Times student revised their approach (RQ3) |
| `score` | `float | None` | Rubric score if graded |
| `success` | `bool | None` | Binary label (rubric ≥ threshold) |
| `rater_scores` | `list[dict]` | `[{rater_id, score}]` for inter-rater reliability |
| `step_details` | `list[dict]` | Per-step breakdown: `[{step_index, time_ms, errors, hints, result}]` |
| `metadata` | `dict` | |

**Cosmos DB container:** `task_attempts`, **partition key:** `/session_id`

---

### 2.4 New Entity: ARCSSurveyResponse

Captures the four ARCS motivational dimensions per session (RQ2).

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID |
| `session_id` | `str` | FK to Session |
| `student_id` | `str` | FK to Student |
| `module_id` | `str` | Which module the survey follows |
| `attention_score` | `float` | ARCS – Attention (1-5 Likert avg) |
| `relevance_score` | `float` | ARCS – Relevance |
| `confidence_score` | `float` | ARCS – Confidence |
| `satisfaction_score` | `float` | ARCS – Satisfaction |
| `composite_score` | `float` | Average of four dimensions |
| `item_responses` | `list[dict]` | `[{item_id, dimension, value, response_time_ms}]` |
| `completion_time_ms` | `int` | Total survey duration |
| `submitted_at` | `datetime` | |
| `metadata` | `dict` | |

**Cosmos DB container:** `arcs_surveys`, **partition key:** `/session_id`

---

### 2.5 New Entity: QualitativeFeedback

Stores open-ended text reflections collected after ARCS surveys (RQ2 Task 2.3).

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID |
| `session_id` | `str` | FK to Session |
| `student_id` | `str` | FK to Student |
| `prompt` | `str` | The question asked |
| `arcs_dimension` | `str | None` | Which ARCS dimension this targets |
| `response_text` | `str` | Student's free-text answer |
| `submitted_at` | `datetime` | |
| `theme_codes` | `list[str]` | Thematic codes assigned during analysis |
| `metadata` | `dict` | |

**Cosmos DB container:** `qualitative_feedback`, **partition key:** `/session_id`

---

### 2.6 New Entity: ClassifierPrediction

Stores the output of the Random Forest classifier for each session (RQ3 Task 3.3).

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID |
| `session_id` | `str` | FK to Session |
| `student_id` | `str` | FK to Student |
| `model_version` | `str` | Identifier of the classifier model used |
| `features_used` | `dict` | The input feature vector: `{time_on_task, hint_frequency, error_count, ...}` |
| `predicted_probability` | `float` | Probability of successful problem-solving (0-1) |
| `predicted_label` | `int` | 0 = failure, 1 = success |
| `actual_label` | `int | None` | Ground truth once rubric scoring is done |
| `actual_score` | `float | None` | Actual rubric score for correlation analysis |
| `confidence_interval` | `dict | None` | `{lower, upper}` 95% CI |
| `created_at` | `datetime` | |
| `metadata` | `dict` | |

**Cosmos DB container:** `classifier_predictions`, **partition key:** `/session_id`

---

## 3. Derived Metrics (computed at query/analysis time)

These are **not stored as raw events** but computed from the telemetry stream for analysis and classifier training.

### 3.1 Session-Level Aggregates (RQ2 behavioral engagement + RQ3 classifier features)

| Metric | Computation | RQ |
|--------|------------|----|
| `persistence_score` | `total_retries / total_errors` (0 if no errors) | RQ2, RQ3 |
| `idle_time_total_ms` | Sum of `IDLE_DETECTED.idle_duration_ms` per session | RQ2, RQ3 |
| `idle_count` | Count of `IDLE_DETECTED` events per session | RQ2, RQ3 |
| `help_rate` | `total_help_requested / session_duration_minutes` | RQ2, RQ3 |
| `help_follow_rate` | `HELP_FOLLOWED / HELP_DELIVERED` | RQ2 |
| `help_by_section` | Count of `HELP_REQUESTED` grouped by `section` | RQ2 |
| `help_by_bot_type` | Count of `HELP_DELIVERED` grouped by `bot_type` | RQ1, RQ2 |
| `error_rate` | `total_errors / total_steps_attempted` | RQ3 |
| `avg_time_per_step_ms` | `mean(TASK_STEP_COMPLETED.time_on_step_ms)` | RQ3 |
| `step_completion_rate` | `total_steps_completed / total_steps_available` | RQ3 |
| `trajectory_revision_count` | Count of trajectory revisions across all tasks | RQ3 |
| `sections_visited_count` | Distinct `SECTION_ENTERED` sections | RQ1 |
| `time_per_section_ms` | Sum of `SECTION_EXITED.time_in_section_ms` per section | RQ2 |
| `normalized_gain` | `(post - pre) / (max - pre)` from Assessment | RQ1 |

### 3.2 Random Forest Classifier Feature Vector (RQ3)

These features feed the scikit-learn RandomForestClassifier:

```python
feature_vector = {
    "time_on_task_ms": int,          # Total active time
    "idle_time_total_ms": int,       # Cumulative idle time (RQ2 engagement, RQ3 classifier)
    "idle_count": int,               # Number of idle periods detected
    "help_frequency": float,          # Help requests per minute
    "help_follow_rate": float,        # % of help suggestions acted upon
    "bot_type": str,                  # "hardcoded" or "ai"
    "error_count": int,               # Total errors in session
    "error_rate": float,              # Errors per step
    "retry_count": int,               # Total retries
    "persistence_score": float,       # Retries / errors
    "avg_time_per_step_ms": float,    # Mean step duration
    "step_completion_rate": float,    # Completed / total steps
    "trajectory_revisions": int,      # Approach changes
    "sections_visited": int,          # Count of distinct sections visited
    "task_completion_count": int,     # Tasks fully completed
}
```

Target label: `success = 1 if rubric_score >= threshold else 0`

---

## 4. Cosmos DB Container Layout

| Container | Partition Key | Entities Stored | Throughput |
|-----------|--------------|-----------------|------------|
| `students` | `/id` | Student | 400 RU/s |
| `sessions` | `/student_id` | Session | 400 RU/s |
| `assessments` | `/student_id` | Assessment | 400 RU/s |
| `telemetry` | `/session_id` | TelemetryEvent | 1000 RU/s (high volume) |
| `agent_actions` | `/session_id` | AgentAction | 400 RU/s |
| `task_attempts` | `/session_id` | TaskAttempt | 400 RU/s |
| `arcs_surveys` | `/session_id` | ARCSSurveyResponse | 400 RU/s |
| `qualitative_feedback` | `/session_id` | QualitativeFeedback | 400 RU/s |
| `classifier_predictions` | `/session_id` | ClassifierPrediction | 400 RU/s |

---

## 5. Data Flow Architecture

```
Unity VR Client
    │
    ├──► TelemetryEvent stream (event-driven)
    │        ├── Help request/deliver/dismiss/follow (with section, content, bot_type)
    │        ├── Section enter/exit
    │        ├── Task start/step/complete/abandon
    │        ├── Error, retry
    │        └── Quiz answers
    │
    ├──► TaskAttempt (created on TASK_STARTED, updated on steps, finalized on complete)
    │
    ├──► ARCSSurveyResponse (submitted at module boundaries)
    │
    ├──► QualitativeFeedback (submitted after ARCS survey)
    │
    └──► Assessment (pre-test on session start, post-test on session end, transfer post-challenge)

Mentor-Agent Service (hardcoded bot or AI bot)
    │
    ├──► AgentAction (logged every time a bot intervenes, with bot_type)
    │
    └──► ClassifierPrediction (generated per session by analytics pipeline)

Derived Metrics (computed post-session or in real-time for agent triggers)
    │
    ├── Session-level aggregates (persistence_score, help_rate, help_by_section, ...)
    └── Feature vector for Random Forest classifier
```

---

## 6. Unity Integration Contract

The Unity client sends telemetry via REST API:

```
POST /api/telemetry/events
{
    "session_id": "...",
    "student_id": "...",
    "event_type": "HELP_REQUESTED",
    "section": "mars",
    "content": "orbital-mechanics",
    "help_text": "",
    "bot_type": "ai",
    "payload": {
        "task_id": "orbital-trajectory-01",
        "step_index": 2,
        "context": "User asked about escape velocity"
    }
}

POST /api/telemetry/events
{
    "session_id": "...",
    "student_id": "...",
    "event_type": "HELP_DELIVERED",
    "section": "mars",
    "content": "orbital-mechanics",
    "help_text": "Escape velocity depends on the planet's mass...",
    "bot_type": "ai",
    "payload": {
        "task_id": "orbital-trajectory-01",
        "step_index": 2,
        "agent_role": "conceptual"
    }
}

POST /api/telemetry/task-attempts
{
    "session_id": "...",
    "student_id": "...",
    "task_id": "orbital-trajectory-01",
    "task_name": "Design an Orbital Trajectory",
    "task_type": "orbital_trajectory",
    ...
}

POST /api/telemetry/arcs-surveys
{
    "session_id": "...",
    "student_id": "...",
    "module_id": "stellar-evolution",
    "attention_score": 4.2,
    "relevance_score": 3.8,
    "confidence_score": 4.0,
    "satisfaction_score": 4.5,
    "item_responses": [
        {"item_id": "A1", "dimension": "attention", "value": 4, "response_time_ms": 3200},
        ...
    ]
}
```
