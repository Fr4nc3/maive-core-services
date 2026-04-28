---
applyTo: "src/frontend/src/**/*.{ts,tsx}"
description: "MAIVE frontend rules. Use when editing any TypeScript or TSX file under src/frontend/src."
---

# MAIVE Frontend — React + TypeScript Instructions

## Role of the frontend

The flat web client serves **two distinct audiences** in this codebase:

1. **Researcher dashboard** (`/students`, `/sessions`, `/assessments`, `/dashboard`) — admin views for the PhD investigator.
2. **Learner experience** (`/learn` — Phase C1) — the **reference implementation** of how every VR client (Unity, Spatial.io, VRChat) must talk to the backend.

When building or editing the learner experience, treat it as if it were a Unity scene rendered in 2D. Same payloads, same telemetry events, same identity flow. **Other VR clients will mirror this code.**

## API client rule

- All backend calls go through `src/api/client.ts`. Never use `fetch(...)` or `axios` directly inside a component.
- The base URL is read from `import.meta.env.VITE_API_BASE` (default `http://localhost:8000`).
- Always send `(platform, platform_user_id)` on first interaction via `identifyStudent({ platform: 'web', platform_user_id })`.
- Persist the returned `student.id` in `localStorage` under the key `maive.student.id` for the duration of the session.

## Identity flow (web client)

1. On mount, check `localStorage` for `maive.platform_user_id`. If missing, generate `crypto.randomUUID()` and persist it.
2. Call `identifyStudent({ platform: 'web', platform_user_id })`.
3. Store the returned `student.id` in component state and `localStorage`.
4. All subsequent calls (`startSession`, `logTelemetry`, `askBot`) include the student's UUID.

## Telemetry rule

- Use `logTelemetry({ session_id, event_type, planet, section, content, payload })` for every user action that the thesis instruments.
- Event types come from the canonical list in [plan/telemetry-model.md](../../plan/telemetry-model.md). **Do not invent new event types** without updating the telemetry model and adding a `DEC-NNN` entry.

## Bot interaction rule

- Use `askBot({ session_id, planet, section, query, content_topic?, difficulty_level?, help_type? })`.
- The response shape is the same regardless of the experimental condition (static vs AI). The UI must not branch on `bot_type`.

## Component conventions

- Use functional components with hooks. No class components.
- Co-locate component-specific styles in `src/styles/global.css` for now (no CSS modules until styling complexity justifies it).
- Use `react-router-dom` for navigation. Routes are declared in `src/App.tsx`.
- Keep page components in `src/pages/` and reusable UI in `src/components/`.

## TypeScript conventions

- Strict mode is on (see `tsconfig.json`). Do not weaken it.
- Define request/response types in `src/api/types.ts`, not inside components.
- Prefer `type` aliases over `interface` for API payloads (matches Pydantic shape).

## Anti-patterns to reject

- ❌ Calling `fetch` or `axios` from inside a component
- ❌ Hardcoding `http://localhost:8000` anywhere
- ❌ Branching UI logic on `bot_type === "ai"` vs `"hardcoded"` (the API hides this on purpose)
- ❌ Inventing telemetry event types not listed in `plan/telemetry-model.md`
- ❌ Storing PII (email, real name) in localStorage or sending it to the backend
- ❌ Adding a new VR-client-specific endpoint instead of using the unified `/api/bot/ask`

## Lint and build

- After changes: `cd src/frontend && npm run build` — must succeed.
- Treat TypeScript errors as build failures.
