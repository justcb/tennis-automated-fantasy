#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
SOCIAL_PAYLOAD_PATH = BASE_DIR / "dist" / "social" / "latest.json"
STATE_DIR = BASE_DIR / ".automation-state"
STATE_PATH = STATE_DIR / "social-delivery-log.json"
BUFFER_API_URL = "https://api.buffer.com"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"delivered": {}}
    return load_json(STATE_PATH)


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def post_body(url: str, body: bytes, headers: dict[str, str]) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read(2000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        body = exc.read(2000).decode("utf-8", "ignore")
        raise SystemExit(f"request error {exc.code}: {body}") from exc


def post_json(url: str, payload: dict, headers: dict[str, str]) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    return post_body(url, body, headers)


def buffer_graphql(api_key: str, query: str) -> dict[str, Any]:
    status, body = post_json(
        BUFFER_API_URL,
        {"query": query},
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    if status < 200 or status >= 300:
        raise SystemExit(f"buffer error {status}: {body}")
    payload = json.loads(body)
    if payload.get("errors"):
        raise SystemExit(f"buffer graphql error: {payload['errors']}")
    return payload


def get_buffer_channels(api_key: str) -> list[dict[str, Any]]:
    org_query = """
    query GetOrganizations {
      account {
        organizations {
          id
          name
        }
      }
    }
    """
    organizations = buffer_graphql(api_key, org_query)["data"]["account"]["organizations"]
    channels: list[dict[str, Any]] = []
    for org in organizations:
        channel_query = f"""
        query GetChannels {{
          channels(input: {{ organizationId: "{org['id']}" }}) {{
            id
            name
            service
          }}
        }}
        """
        for channel in buffer_graphql(api_key, channel_query)["data"]["channels"]:
            channels.append({**channel, "organizationId": org["id"], "organizationName": org["name"]})
    return channels


def select_channel(channels: list[dict[str, Any]], service_names: set[str], env_id: str) -> dict[str, Any] | None:
    explicit_id = os.environ.get(env_id)
    if explicit_id:
        return next((channel for channel in channels if channel["id"] == explicit_id), None)
    matches = [channel for channel in channels if channel["service"] in service_names]
    if len(matches) == 1:
        return matches[0]
    return None


def create_buffer_post(api_key: str, text: str, channel_id: str, mode: str, image_url: str | None = None) -> None:
    assets_block = ""
    if image_url:
        assets_block = f"""
        assets: {{
          images: [
            {{
              url: "{image_url}"
            }}
          ]
        }}
        """
    mutation = f"""
    mutation CreatePost {{
      createPost(input: {{
        text: {json.dumps(text)}
        channelId: "{channel_id}"
        schedulingType: automatic
        mode: {mode}
        {assets_block}
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
          }}
        }}
        ... on MutationError {{
          message
        }}
      }}
    }}
    """
    payload = buffer_graphql(api_key, mutation)["data"]["createPost"]
    if payload.get("message"):
        raise SystemExit(f"buffer createPost error: {payload['message']}")


def deliver_via_webhook(payload: dict[str, Any]) -> bool:
    webhook = os.environ.get("SOCIAL_WEBHOOK_URL")
    if not webhook:
        return False

    timestamp = str(int(time.time()))
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "tennis-automated-social/1.0",
        "X-Tennis-Automated-Event": "cheat-sheet-published",
        "X-Tennis-Automated-Timestamp": timestamp,
    }
    secret = os.environ.get("SOCIAL_WEBHOOK_SECRET")
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if secret:
        signed = f"{timestamp}.".encode("utf-8") + body
        signature = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        headers["X-Tennis-Automated-Signature"] = f"sha256={signature}"

    status, response_body = post_body(webhook, body, headers)
    if status < 200 or status >= 300:
        raise SystemExit(f"webhook error {status}: {response_body}")
    return True


def deliver_via_buffer(payload: dict[str, Any]) -> bool:
    api_key = os.environ.get("BUFFER_API_KEY")
    if not api_key:
        return False

    channels = get_buffer_channels(api_key)
    x_channel = select_channel(channels, {"twitter", "x"}, "BUFFER_X_CHANNEL_ID")
    instagram_channel = select_channel(channels, {"instagram"}, "BUFFER_INSTAGRAM_CHANNEL_ID")

    if not x_channel:
        raise SystemExit("buffer setup error: could not resolve X channel; set BUFFER_X_CHANNEL_ID")

    create_buffer_post(api_key, payload["x_text"], x_channel["id"], "shareNow")
    if instagram_channel:
        create_buffer_post(api_key, payload["instagram_caption"], instagram_channel["id"], "shareNow", payload["image_url"])
    else:
        print("skip: no Instagram channel connected in Buffer")
    return True


def main(argv: list[str]) -> int:
    force = "--force" in argv[1:]

    payload = load_json(SOCIAL_PAYLOAD_PATH)
    delivery_key = payload["post_key"]
    state = load_state()
    delivered = state.setdefault("delivered", {})
    if delivered.get(delivery_key) and not force:
        print(f"skip: {delivery_key} already delivered")
        return 0

    delivered_now = False
    if deliver_via_webhook(payload):
        delivered_now = True
    elif deliver_via_buffer(payload):
        delivered_now = True
    else:
        print("skip: neither SOCIAL_WEBHOOK_URL nor BUFFER_API_KEY is configured")
        return 0

    if delivered_now:
        delivered[delivery_key] = {
            "week": payload["week"],
            "label": payload["label"],
            "updated_at": payload["updated_at"],
        }
        save_state(state)
        print(f"delivered {delivery_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
