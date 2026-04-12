#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import build_week


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def resolve_target(arg: str) -> Path:
    path = Path(arg)
    if not path.is_absolute():
        path = BASE_DIR / arg
    return path.resolve()


def promote(target_path: Path) -> list[Path]:
    if not target_path.exists():
        raise SystemExit(f"Target not found: {target_path}")

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    changed: list[Path] = []
    for path in sorted(DATA_DIR.glob("*.json")):
        payload = load_json(path)
        publish = payload["publish"]
        new_live = path == target_path
        new_draft = False if new_live else publish.get("draft", False)
        if publish.get("live") != new_live or publish.get("draft", False) != new_draft:
            publish["live"] = new_live
            if new_draft:
                publish["draft"] = True
            elif "draft" in publish:
                publish["draft"] = False
            changed.append(path)
        if new_live and publish["updated_at"] != now:
            publish["updated_at"] = now
            if path not in changed:
                changed.append(path)
        write_json(path, payload)
    return changed


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("Usage: python3 publish_week.py data/week-3.json")

    target_path = resolve_target(argv[1])
    changed = promote(target_path)
    build_week.build_all(sorted(DATA_DIR.glob("*.json")))

    print(f"promoted {target_path}")
    for path in changed:
        print(f"updated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
