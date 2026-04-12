#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOCIAL_PAYLOAD_PATH = BASE_DIR / "dist" / "social" / "latest.json"
STATE_DIR = BASE_DIR / ".automation-state"
STATE_PATH = STATE_DIR / "social-delivery-log.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"delivered": {}}
    return load_json(STATE_PATH)


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def main(argv: list[str]) -> int:
    force = "--force" in argv[1:]
    webhook = os.environ.get("SOCIAL_WEBHOOK_URL")
    if not webhook:
        print("skip: SOCIAL_WEBHOOK_URL is not configured")
        return 0

    payload = load_json(SOCIAL_PAYLOAD_PATH)
    delivery_key = payload["post_key"]
    state = load_state()
    delivered = state.setdefault("delivered", {})
    if delivered.get(delivery_key) and not force:
        print(f"skip: {delivery_key} already delivered")
        return 0

    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = response.read(400).decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        body = exc.read(400).decode("utf-8", "ignore")
        raise SystemExit(f"webhook error {exc.code}: {body}") from exc

    if status < 200 or status >= 300:
        raise SystemExit(f"webhook error {status}: {body}")

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
