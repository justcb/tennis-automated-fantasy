# Tennis Automated Fantasy Pages

This folder now supports repeatable weekly ATP Fantasy cheat sheets from structured JSON data.

## Files

- `build_week.py`: builds one or more weekly pages
- `data/week-2.json`: Week 2 content source
- `week-2.html`: generated customer-facing page
- `dist/`: publish-ready static output for hosting
- `publish-config.json`: public hosting base URL
- `squarespace-code-block.html`: one-time embed snippet for Squarespace
- `weekly-model.md`: editorial and data model notes

## Workflow

1. Copy an existing week JSON file in `data/`.
2. Update the hero copy, tournament lens, stats, and pick sections.
3. Set the output filename in the JSON.
4. Rebuild the page.
5. Deploy the contents of `dist/` to static hosting.

## Build

Build every week in `data/`:

```bash
python3 /Users/studio/tennis-automated-fantasy/build_week.py
```

Build one file:

```bash
python3 /Users/studio/tennis-automated-fantasy/build_week.py /Users/studio/tennis-automated-fantasy/data/week-2.json
```

## Publish Output

The build writes:

- `dist/pages/<versioned-file>.html`
- `dist/manifest/latest.json`
- `dist/manifest/archive.json`
- `dist/index.html`
- `dist/_headers`

`latest.json` is the live pointer that Squarespace should load.

## Live Switching

Each week JSON file includes:

- `publish.filename`
- `publish.week`
- `publish.label`
- `publish.updated_at`
- `publish.live`

Exactly one file should have `publish.live = true`.

Recommended pattern:

- Monday pre-draw file becomes live.
- Saturday draw-update file is published as a new version and becomes live.
- The previous file stays in the archive.

## Squarespace

Paste the contents of `squarespace-code-block.html` into a Squarespace Code Block on your permanent cheat sheet page. That snippet fetches `manifest/latest.json`, loads the current hosted page in an iframe, and resizes it automatically.

## Hosting

`netlify.toml` is included for Netlify. Point the site at this folder/repo and publish `dist/`.

## Content Schema

Top-level fields:

- `page_title`
- `eyebrow`
- `headline`
- `dek`
- `meta`
- `blocks`
- `footer_note`
- `output`
- `archive_summary`
- `publish`

Supported block types:

- `two-col-list`
- `grid`

Supported card kinds inside `grid`:

- `rich-text`
- `pick-list`

The generator intentionally keeps the schema small so each new week is mostly a content task, not a coding task.
