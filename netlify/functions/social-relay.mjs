import crypto from "node:crypto";

import { getStore } from "@netlify/blobs";


const BUFFER_API_URL = "https://api.buffer.com";
const STORE_NAME = "social-relay";
const MAX_AGE_SECONDS = 900;


function jsonResponse(status, payload) {
  return new Response(JSON.stringify(payload, null, 2) + "\n", {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}


function timingSafeEqual(a, b) {
  const aBuffer = Buffer.from(a);
  const bBuffer = Buffer.from(b);
  if (aBuffer.length !== bBuffer.length) {
    return false;
  }
  return crypto.timingSafeEqual(aBuffer, bBuffer);
}


function verifySignature(rawBody, headers) {
  const secret = process.env.SOCIAL_WEBHOOK_SECRET;
  if (!secret) {
    return { ok: false, error: "SOCIAL_WEBHOOK_SECRET is not configured" };
  }

  const timestamp = headers.get("x-tennis-automated-timestamp");
  const signature = headers.get("x-tennis-automated-signature");
  if (!timestamp || !signature) {
    return { ok: false, error: "Missing signature headers" };
  }

  const age = Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp));
  if (!Number.isFinite(age) || age > MAX_AGE_SECONDS) {
    return { ok: false, error: "Webhook timestamp is stale" };
  }

  const expected = crypto
    .createHmac("sha256", secret)
    .update(`${timestamp}.${rawBody}`)
    .digest("hex");
  const provided = signature.replace(/^sha256=/, "");
  if (!timingSafeEqual(expected, provided)) {
    return { ok: false, error: "Invalid webhook signature" };
  }

  return { ok: true };
}


async function bufferGraphql(apiKey, query) {
  const response = await fetch(BUFFER_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
      "Accept": "application/json",
      "User-Agent": "tennis-automated-relay/1.0",
      "Origin": "https://developers.buffer.com",
      "Referer": "https://developers.buffer.com/",
    },
    body: JSON.stringify({ query }),
  });

  const text = await response.text();
  let payload = {};
  try {
    payload = JSON.parse(text);
  } catch {
    payload = { raw: text };
  }

  if (!response.ok) {
    throw new Error(`Buffer HTTP ${response.status}: ${text}`);
  }
  if (payload.errors) {
    throw new Error(`Buffer GraphQL error: ${JSON.stringify(payload.errors)}`);
  }
  return payload;
}


async function getBufferChannels(apiKey) {
  const orgQuery = `
    query GetOrganizations {
      account {
        organizations {
          id
          name
        }
      }
    }
  `;
  const organizations = (await bufferGraphql(apiKey, orgQuery)).data.account.organizations;
  const channels = [];

  for (const organization of organizations) {
    const channelQuery = `
      query GetChannels {
        channels(input: { organizationId: "${organization.id}" }) {
          id
          name
          service
        }
      }
    `;
    const channelPayload = await bufferGraphql(apiKey, channelQuery);
    for (const channel of channelPayload.data.channels) {
      channels.push({
        ...channel,
        organizationId: organization.id,
        organizationName: organization.name,
      });
    }
  }
  return channels;
}


function selectChannel(channels, services, explicitId) {
  if (explicitId) {
    return channels.find((channel) => channel.id === explicitId) ?? null;
  }
  const matches = channels.filter((channel) => services.has(channel.service));
  if (matches.length === 1) {
    return matches[0];
  }
  return null;
}


async function createBufferPost(apiKey, { text, channelId, imageUrl = null }) {
  const assetsBlock = imageUrl
    ? `
        assets: {
          images: [
            {
              url: "${imageUrl}"
            }
          ]
        }
      `
    : "";

  const mutation = `
    mutation CreatePost {
      createPost(input: {
        text: ${JSON.stringify(text)}
        channelId: "${channelId}"
        schedulingType: automatic
        mode: shareNow
        ${assetsBlock}
      }) {
        ... on PostActionSuccess {
          post {
            id
          }
        }
        ... on MutationError {
          message
        }
      }
    }
  `;

  const payload = (await bufferGraphql(apiKey, mutation)).data.createPost;
  if (payload.message) {
    throw new Error(`Buffer createPost error: ${payload.message}`);
  }
  return payload.post.id;
}


export default async (request) => {
  if (request.method !== "POST") {
    return jsonResponse(405, { error: "Method not allowed" });
  }

  const verification = verifySignature(await request.clone().text(), request.headers);
  if (!verification.ok) {
    return jsonResponse(401, { error: verification.error });
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return jsonResponse(400, { error: "Invalid JSON payload" });
  }

  const required = ["post_key", "week", "label", "url", "x_text"];
  for (const field of required) {
    if (!payload[field]) {
      return jsonResponse(400, { error: `Missing field: ${field}` });
    }
  }

  const store = getStore(STORE_NAME);
  const dedupeKey = `delivered:${payload.post_key}`;
  const prior = await store.get(dedupeKey, { type: "json" });
  if (prior) {
    return jsonResponse(200, {
      ok: true,
      status: "duplicate",
      post_key: payload.post_key,
      delivered_at: prior.delivered_at,
    });
  }

  const apiKey = process.env.BUFFER_API_KEY;
  if (!apiKey) {
    return jsonResponse(500, { error: "BUFFER_API_KEY is not configured" });
  }

  try {
    const channels = await getBufferChannels(apiKey);
    const xChannel = selectChannel(channels, new Set(["twitter", "x"]), process.env.BUFFER_X_CHANNEL_ID);
    const instagramChannel = selectChannel(channels, new Set(["instagram"]), process.env.BUFFER_INSTAGRAM_CHANNEL_ID);

    if (!xChannel) {
      return jsonResponse(500, { error: "Could not resolve Buffer X channel" });
    }

    const xPostId = await createBufferPost(apiKey, {
      text: payload.x_text,
      channelId: xChannel.id,
    });

    let instagram = { status: "skipped", reason: "No Instagram channel connected" };
    if (instagramChannel && payload.instagram_caption && payload.image_url) {
      const instagramPostId = await createBufferPost(apiKey, {
        text: payload.instagram_caption,
        channelId: instagramChannel.id,
        imageUrl: payload.image_url,
      });
      instagram = { status: "posted", post_id: instagramPostId };
    }

    const delivered = {
      delivered_at: new Date().toISOString(),
      week: payload.week,
      label: payload.label,
      x_post_id: xPostId,
      instagram,
    };
    await store.setJSON(dedupeKey, delivered);

    return jsonResponse(200, {
      ok: true,
      status: "posted",
      post_key: payload.post_key,
      x: { status: "posted", post_id: xPostId },
      instagram,
    });
  } catch (error) {
    return jsonResponse(502, {
      error: error instanceof Error ? error.message : String(error),
      post_key: payload.post_key,
    });
  }
};
