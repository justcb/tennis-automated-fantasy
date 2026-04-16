#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"


def run(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=str(cwd), text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    if not DIST_DIR.exists():
        raise SystemExit("dist/ does not exist. Run build_week.py first.")

    remote_url = subprocess.check_output(
        ["git", "remote", "get-url", "origin"],
        cwd=str(BASE_DIR),
        text=True,
    ).strip()

    with tempfile.TemporaryDirectory(prefix="ta-gh-pages-") as tmp:
        tmp_path = Path(tmp)
        for item in DIST_DIR.iterdir():
            target = tmp_path / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

        run(["git", "init", "-b", "gh-pages"], tmp_path)
        run(["git", "config", "user.name", "Studio Server"], tmp_path)
        run(["git", "config", "user.email", "studio@Studios-Mac-Studio.local"], tmp_path)
        run(["git", "add", "."], tmp_path)
        run(["git", "commit", "-m", "Publish GitHub Pages"], tmp_path)
        run(["git", "remote", "add", "origin", remote_url], tmp_path)
        run(["git", "push", "--force", "origin", "gh-pages"], tmp_path)

    print("published dist/ to origin gh-pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
