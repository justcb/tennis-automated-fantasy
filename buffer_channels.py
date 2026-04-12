#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

from deliver_social import get_buffer_channels


def main(argv: list[str]) -> int:
    api_key = os.environ.get("BUFFER_API_KEY")
    if not api_key:
        raise SystemExit("BUFFER_API_KEY is not configured")

    channels = get_buffer_channels(api_key)
    print(json.dumps(channels, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
