# Tennis Automated Fantasy Pages

This folder now supports repeatable weekly ATP Fantasy cheat sheets from structured JSON data.

## Files

- `build_week.py`: builds one or more weekly pages
- `publish_week.py`: promotes a chosen week file live and rebuilds output
- `deliver_social.py`: sends the current social payload to a webhook with dedupe
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
4. If the page is only a future scaffold, set `publish.draft` to `true`.
5. Rebuild the page.
6. Deploy the contents of `dist/` to static hosting.

## Build

Build every week in `data/`:

```bash
python3 /Users/studio/tennis-automated-fantasy/build_week.py
```

Build one file:

```bash
python3 /Users/studio/tennis-automated-fantasy/build_week.py /Users/studio/tennis-automated-fantasy/data/week-2.json
```

Promote a week live and rebuild everything:

```bash
python3 /Users/studio/tennis-automated-fantasy/publish_week.py /Users/studio/tennis-automated-fantasy/data/week-3.json
```

Deliver the generated social payload to your webhook:

```bash
SOCIAL_WEBHOOK_URL="https://hooks.example.com/..." \
python3 /Users/studio/tennis-automated-fantasy/deliver_social.py
```

## Publish Output

The build writes:

- `dist/pages/<versioned-file>.html`
- `dist/manifest/latest.json`
- `dist/manifest/archive.json`
- `dist/index.html`
- `dist/_headers`
- `dist/social/latest.json`
- `dist/social/latest-x.txt`
- `dist/social/latest-instagram.txt`

`latest.json` is the live pointer that Squarespace should load.
`dist/social/latest.json` is the machine-readable announcement payload for the current live page.

## Live Switching

Each week JSON file includes:

- `publish.filename`
- `publish.week`
- `publish.label`
- `publish.updated_at`
- `publish.live`

Exactly one file should have `publish.live = true`.

If a future week should exist locally but stay out of Netlify and the public archive, add:

- `publish.draft = true`

Recommended pattern:

- Monday pre-draw file becomes live.
- Saturday draw-update file is published as a new version and becomes live.
- The previous file stays in the archive.
- Future scaffolds stay local as drafts until you are ready to publish them.

## Social Automation

The build generates current announcement copy for:

- X in `dist/social/latest-x.txt`
- Instagram in `dist/social/latest-instagram.txt`
- webhook automation in `dist/social/latest.json`

`deliver_social.py` posts that JSON payload to `SOCIAL_WEBHOOK_URL` and stores a local dedupe log in `.automation-state/` so the same page version is not announced twice.

Recommended production path:

1. Connect X and Instagram to Buffer.
2. Use Zapier or Make to receive `dist/social/latest.json`.
3. Have that workflow create posts in Buffer for both channels.

This is more robust than direct browser automation and avoids maintaining separate X and Instagram API integrations inside this repo.

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
