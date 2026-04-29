# Help Content — Static Bot Responses (Control Group)

Static, hand-curated bot responses used by the **non-adaptive VR control
condition**. The `/api/bot/ask` endpoint queries this collection when
`session.condition == "non-adaptive-vr"`.

## Structure
```
data/help_content/
  <planet>/
    <topic>.json   # one or many HelpContent records
```

- Folder name = `planet` (Cosmos partition key for the `help_content` container)
- Each JSON file contains either a single object or a list of objects matching
  `HelpContent` (see [`src/backend/app/domain/entities/help_content.py`](../../src/backend/app/domain/entities/help_content.py)).
- Both languages live in the same file; differentiate via the `tags`
  array (e.g. `"en"`, `"es"`) and use a localised `title` / `body_text`.
  The `language` discriminator at query time is the session's
  `language_preference` field.

## Required fields
- `planet` — partition key (defaults to folder name if absent)
- `section` — area within planet (e.g. `crater_lab`)
- `content_topic` — semantic topic (e.g. `atmosphere`, `orbital-mechanics`)
- `difficulty_level` — `easy` / `medium` / `hard`
- `help_type` — `hint` / `explanation` / `fact` / `quiz_feedback`
- `title`, `body_text`

## Seed
```
cd src/backend
uv run python -m app.cli.seed_help_content              # all planets
uv run python -m app.cli.seed_help_content --planet mars
```

## Coverage seed (Phase S)
- `mars/atmosphere.json` — 6 records (3 EN + 3 ES; `fact`, `hint`, `explanation`)

Add new planets / topics by creating a new folder and JSON file, then
re-run the seeder. The seeder is idempotent on `id` (`create_item` will
fail on duplicates — re-seed only into a clean container).
