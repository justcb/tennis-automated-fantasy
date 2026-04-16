# Tennis Automated Fantasy Pages

This folder now supports repeatable weekly ATP Fantasy cheat sheets from structured JSON data.

## Files

- `build_week.py`: builds one or more weekly pages
- `publish_week.py`: promotes a chosen week file live and rebuilds output
- `deliver_social.py`: sends the current social payload to a signed webhook relay or Buffer with dedupe
- `buffer_channels.py`: lists connected Buffer channels from `BUFFER_API_KEY`
- `social-relay.md`: webhook relay contract and verification notes
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
SOCIAL_WEBHOOK_URL="https://your-relay.example.com/social" \
SOCIAL_WEBHOOK_SECRET="shared-secret" \
python3 /Users/studio/tennis-automated-fantasy/deliver_social.py
```

List the Buffer channels available to the API key:

```bash
BUFFER_API_KEY="..." \
python3 /Users/studio/tennis-automated-fantasy/buffer_channels.py
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
- `dist/social/latest-instagram-card.png`

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

If a future week should exist locally but stay out of the public site and archive, add:

- `publish.draft = true`

Recommended pattern:

- Monday results file becomes live.
- Wednesday next-week pre-draw file becomes live.
- Saturday draw-update file is published as a new version and becomes live.
- The previous file stays in the archive.
- Future scaffolds stay local as drafts until you are ready to publish them.

## Social Automation

The build generates current announcement copy for:

- X in `dist/social/latest-x.txt`
- Instagram in `dist/social/latest-instagram.txt`
- Instagram image in `dist/social/latest-instagram-card.png`
- webhook automation in `dist/social/latest.json`

Preferred production path:

- set `SOCIAL_WEBHOOK_URL`
- set `SOCIAL_WEBHOOK_SECRET`
- let your relay post to Buffer, X, and Instagram

`deliver_social.py` signs outbound webhook requests when `SOCIAL_WEBHOOK_SECRET` is set.

Netlify relay path in this repo:

- endpoint: `/api/social-relay`
- function source: `netlify/functions/social-relay.mjs`
- dedupe store: Netlify Blobs store `social-relay`

Direct Buffer fallback:

`deliver_social.py` can also try native Buffer posting when `BUFFER_API_KEY` is configured. It auto-discovers channels when there is only one X channel and one Instagram channel on the account. If there are multiple, set:

- `BUFFER_X_CHANNEL_ID`
- `BUFFER_INSTAGRAM_CHANNEL_ID`

Webhook delivery is attempted before direct Buffer delivery.

The script stores a local dedupe log in `.automation-state/` so the same page version is not announced twice.
If only X is connected in Buffer, the script will still post to X and skip Instagram without failing.

Recommended production path:

1. Build and publish the cheat sheet from this repo.
2. Send `dist/social/latest.json` to the Netlify relay with `deliver_social.py`.
3. Have the relay verify the signature, dedupe on `post_key`, and post to social.
4. Let Buffer or native platform integrations live only in the relay.

Fallback path:

1. Set `BUFFER_API_KEY`.
2. Let `deliver_social.py` post directly to Buffer when the relay is unavailable.

## Squarespace

Paste the contents of `squarespace-code-block.html` into a Squarespace Code Block on your permanent cheat sheet page. That snippet fetches `manifest/latest.json`, loads the current hosted page in an iframe, and resizes it automatically.

## Hosting

Primary path:

- GitHub Pages via the `gh-pages` branch
- custom domain target: `https://fantasy.tennisautomated.com`

This repo is now set up to publish the `dist/` directory directly to the `gh-pages` branch.

One-time GitHub setup:

1. In the repo settings, set Pages source to `Deploy from a branch`.
2. Select branch `gh-pages` and folder `/ (root)`.
3. Add the custom domain `fantasy.tennisautomated.com`.
4. Point DNS for `fantasy.tennisautomated.com` to GitHub Pages as a `CNAME` to `justcb.github.io`.

Deploy command:

```bash
python3 /Users/studio/tennis-automated-fantasy/build_week.py
python3 /Users/studio/tennis-automated-fantasy/deploy_gh_pages.py
```

The build writes a `CNAME` file into `dist/`, so the custom domain follows the published branch cleanly.

If you prefer a completely manual branch deploy, the same approach can be done by copying `dist/` to `gh-pages`, but `deploy_gh_pages.py` keeps that repeatable.

Legacy path:

- `netlify.toml` remains in the repo, but Netlify is no longer the primary site host.

If you still want the relay function somewhere managed, host the social relay separately from the site.

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
