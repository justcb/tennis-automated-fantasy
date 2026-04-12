# Social Relay

Use a webhook relay as the primary social delivery path.

In this repo, the relay is implemented as a Netlify Function at:

- `netlify/functions/social-relay.mjs`
- public path `/api/social-relay`

## Why

- publishing stays in this repo
- social posting moves to a service with stable network identity
- Buffer, X, and Instagram credentials stay out of the build machine
- retries and delivery logs live in the relay, not in the page generator

## Inputs From This Repo

`deliver_social.py` sends `dist/social/latest.json` to `SOCIAL_WEBHOOK_URL`.

Headers:

- `Content-Type: application/json`
- `User-Agent: tennis-automated-social/1.0`
- `X-Tennis-Automated-Event: cheat-sheet-published`
- `X-Tennis-Automated-Timestamp: <unix-seconds>`
- `X-Tennis-Automated-Signature: sha256=<hex>` if `SOCIAL_WEBHOOK_SECRET` is set

Body fields:

- `site_title`
- `post_key`
- `week`
- `label`
- `updated_at`
- `url`
- `image_url`
- `source`
- `x_text`
- `instagram_caption`

## Signature Verification

If `SOCIAL_WEBHOOK_SECRET` is configured, verify:

1. build the string `<timestamp>.<raw_json_body>`
2. compute HMAC-SHA256 using the shared secret
3. compare to `X-Tennis-Automated-Signature`

Reject requests with stale timestamps.

## Relay Behavior

Recommended relay behavior:

1. verify the signature
2. dedupe on `post_key`
3. send `x_text` to the X publishing step
4. send `instagram_caption` plus `image_url` to the Instagram publishing step
5. log success or failure by `post_key`

The Netlify implementation stores dedupe records in the Blobs store:

- store name: `social-relay`
- key pattern: `delivered:<post_key>`

## Netlify Environment Variables

Required:

- `BUFFER_API_KEY`
- `SOCIAL_WEBHOOK_SECRET`

Optional:

- `BUFFER_X_CHANNEL_ID`
- `BUFFER_INSTAGRAM_CHANNEL_ID`

If only one X channel is connected in Buffer, the relay auto-discovers it. If no Instagram channel is connected, the relay skips Instagram and still posts to X.

## Practical Targets

Common relay options:

- Zapier webhook -> Buffer/X/Instagram actions
- Make custom webhook -> Buffer/X/Instagram modules
- a small serverless function that calls Buffer or native platform APIs

## Repo Fallback

If `SOCIAL_WEBHOOK_URL` is not set, `deliver_social.py` can still try direct Buffer posting when `BUFFER_API_KEY` is configured. That is a fallback, not the preferred production path.
