# Stella Astra — character assets

Drop the final animated GIFs here, named exactly:

| File              | When it plays                                       |
|-------------------|-----------------------------------------------------|
| `idle.gif`        | Default — Stella waiting for the learner            |
| `thinking.gif`    | Bot request in flight (`busy = true`)               |
| `talking.gif`     | Reply just rendered                                 |
| `celebrating.gif` | Optional — assessment completed / mastery reached   |

Vite serves `/public/*` at `/`, so the component references them as
`/stella/idle.gif`, `/stella/thinking.gif`, …

While real GIFs are not yet authored, animated SVG placeholders with the
same base names live alongside this README and are loaded by the
`<StellaAstra>` component as a fallback when the `.gif` file is missing.

**Design brief (PhD MAIVE)**: Stella Astra is the friendly mentor avatar
of the multi-agent system. The character name is shared across EN/ES per
DEC-014 — only the speech-bubble copy is translated.
