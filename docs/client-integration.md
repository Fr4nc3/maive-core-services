# Client Integration Guide

The MAIVE backend exposes a **single contract** that all VR clients
share. This document describes how each platform plugs into that
contract.

## Common contract (all platforms)

Every learner client follows the same three-step lifecycle:

### 1. Identify the user

```
POST /api/users/identify
{
  "platform": "spatial.io" | "vrchat" | "sinespace" | "web",
  "platform_user_id": "<stable id from the host platform>",
  "display_name": "<optional>",
  "condition": "control" | "treatment"   # only on first identify
}
```

Idempotent — returns the existing user if the
`(platform, platform_user_id)` pair is already known. See **DEC-009**.

### 2. Open a session

```
POST /api/sessions
{ "user_id": "<uuid>", "condition": "control" | "treatment" }
```

### 3. Stream telemetry + ask the bot

```
POST /api/telemetry          # for every behavioral event
POST /api/bot/ask            # unified — server picks static vs. AI by session.condition
```

The `/api/bot/ask` response is identical across conditions:

```json
{ "source": "static" | "ai", "answer": "...", "metadata": {} }
```

Clients should **not** branch on condition themselves — that is a
backend concern (DEC-008).

---

## C2. Unity SDK

**Status:** planned (sandbox at `src/unity/sandbox_26`).

Implementation pattern:

- A C# `MaiveClient` wrapper around `UnityWebRequest` (or
  `HttpClient`) targeting `MAIVE_API_BASE_URL`.
- Identity resolved from the local Unity build (e.g. command-line
  arg `--user-id` for desktop test, or platform SDK id when embedded
  in a host).
- Telemetry buffered and flushed every N seconds or on scene change
  to avoid blocking the render loop.
- Bot UI rendered as a world-space canvas; the bot reply is read
  aloud via Unity TTS or shown as floating text.

Recommended event types to emit:
`session_start`, `section_enter`, `section_exit`, `task_attempt`,
`help_request`, `bot_reply_shown`, `survey_submitted`,
`session_end`.

## C3. Spatial.io

**Status:** research (DEC-008 — Spatial.io API limitations).

Spatial.io exposes a sandboxed scripting environment with limited
network access and no persistent backend bridge. The current plan:

- Use the official Spatial Toolkit visual scripts where possible.
- For events that cannot be sent directly, mirror them via a
  companion **web page** (the `/learner` page in this repo) opened in
  the user's browser, using a shared `platform_user_id`.
- Document each missing capability in `docs/decisions.md` so the
  thesis can cite the constraint.

## C4. VRChat (hybrid)

**Status:** planned.

VRChat worlds (Udon) cannot make arbitrary HTTP calls. Pattern:

- Inside the world, capture events with Udon and serialize to a
  string-encoded payload.
- A **mirror web client** (browser tab opened by the participant
  before donning the headset) polls the world state via VRChat's
  string loaders or a side channel and forwards events to the
  MAIVE backend.
- Identity is bound by asking the participant to enter a short code
  shown in-world into the web client.

This hybrid approach is documented as a constraint in the systems
engineering paper (`docs/paper/`).

---

## Reference client

The web reference client at `src/frontend/src/pages/LearnerPage.tsx`
implements the full contract end-to-end and is the canonical example
when porting to a new platform.
