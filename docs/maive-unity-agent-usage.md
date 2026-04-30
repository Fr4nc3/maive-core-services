# MAIVE Unity Agent Usage

Use `@maive-unity` for planning the Unity serious-game core of MAIVE, especially the migration away from Spatial.io now that Spatial.io is closing and no real replacement platform has been found.

The agent creates plans, inventories, SDK comparisons, and Unity Editor handoff checklists. It does not assume Copilot or agents can operate inside Unity.

## Unity Project Links

Folders under `src/unity` are symbolic links to different real Unity projects for MAIVE. When working with Unity, `@maive-unity` should first identify each linked project root and target filesystem path, verify the Unity version and `Packages/manifest.json`, and decide whether each project is reference material or the active migration target. This prevents accidental writes through a link into the wrong Unity project.

## Manual Trigger

Invoke the agent directly in chat with:

```text
@maive-unity
```

Example:

```text
@maive-unity Inventory the Unity elements needed for the MAIVE single-player astronomy serious game now that Spatial.io is closing.
```

## Automatic Trigger Phrases

The workspace dispatcher should route to `@maive-unity` when a request mentions:

- Unity
- `src/unity`
- serious game
- Spatial.io closing
- Spatial.io sunset
- migration off Spatial.io
- Spatial.io-like open world
- single-player Unity
- character controller
- SDK selection
- Unity SDK
- `MaiveClient.cs`
- VR client telemetry
- open-world astronomy

## Use It For

- Planning MAIVE's standalone Unity replacement for Spatial.io.
- Identifying Unity scene, prefab, controller, UI, telemetry, and bot-integration elements.
- Comparing character-controller, XR, navigation, web request, and open-world SDK options.
- Mapping Unity interactions to MAIVE telemetry and RQ1/RQ2/RQ3.
- Drafting manual Unity Editor implementation checklists.
- Explaining which Spatial.io assets or patterns can be reused as references without depending on Spatial hosting.
- Mapping linked Unity projects under `src/unity` and deciding which are reference material versus the active migration target.

## Do Not Use It For

- Editing linked Unity project roots, scenes, prefabs, packages, or C# scripts by default.
- Backend RAI pipeline work; use `@maive-rai`.
- React dashboard work; use `@maive-frontend`.
- Azure deployment or infrastructure work; use `@maive-deploy`.
- Research statistics, ARCS methodology, or thesis claims; use `@maive-research`.
- General cross-cutting backend architecture; use `@maive-lead`.

## Example Prompts

```text
@maive-unity Create a migration plan from Spatial.io to standalone Unity for MAIVE.
```

```text
@maive-unity Compare Unity Starter Assets, XR Interaction Toolkit, Cinemachine, and other controller SDKs for the MAIVE open-world astronomy game.
```

```text
@maive-unity Map the Unity serious-game interactions to telemetry events for RQ1, RQ2, and RQ3.
```

```text
@maive-unity Draft the MaiveClient.cs responsibilities for identity, session, telemetry, and bot calls.
```

```text
@maive-unity Identify what Unity elements Francia needs to implement manually in the Editor.
```

## Expected Outputs

Depending on the prompt, the agent should return one or more of:

- Unity serious-game element inventory
- Spatial.io exit and migration rationale
- SDK/package decision matrix
- Unity scene/module blueprint
- `MaiveClient.cs` responsibility outline
- telemetry-to-RQ mapping
- manual Unity Editor implementation checklist
- risks and verification steps

## Handoff To Unity Editor Work

`@maive-unity` should stop at implementation-ready guidance unless explicitly asked to edit Unity project files. The expected handoff is a clear checklist that Francia can apply in Unity, including which scenes, prefabs, packages, scripts, and inspector settings to create or verify.

For MAIVE integration, the agent must preserve the shared backend contract:

- `platform = "unity"`
- `POST /api/users/identify`
- `POST /api/sessions`
- `POST /api/telemetry`
- `POST /api/bot/ask`
- conditions: `maive | non-adaptive-vr`

Unity-specific plans must also preserve the no-PII rule: users are identified only by `(platform, platform_user_id)` plus the backend internal UUID, with optional `display_name`.
