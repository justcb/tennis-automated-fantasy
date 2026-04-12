#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DIST_DIR = BASE_DIR / "dist"
PAGES_DIR = DIST_DIR / "pages"
MANIFEST_DIR = DIST_DIR / "manifest"
CONFIG_PATH = BASE_DIR / "publish-config.json"


DEFAULT_CONFIG = {
    "public_base_url": "https://fantasy.tennisautomated.com",
    "site_title": "Tennis Automated Fantasy",
}


STYLE = """\
      :root {
        --bg: #f3eee4;
        --paper: #fffaf2;
        --ink: #11211d;
        --muted: #52605c;
        --accent: #c65a18;
        --accent-2: #1d6b52;
        --line: rgba(17, 33, 29, 0.14);
        --shadow: 0 20px 50px rgba(17, 33, 29, 0.12);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(198, 90, 24, 0.12), transparent 28%),
          radial-gradient(circle at top right, rgba(29, 107, 82, 0.12), transparent 32%),
          linear-gradient(180deg, #efe5d4 0%, var(--bg) 100%);
      }

      .wrap {
        width: min(1100px, calc(100% - 32px));
        margin: 0 auto;
        padding: 32px 0 56px;
      }

      .hero {
        background: linear-gradient(135deg, rgba(17, 33, 29, 0.96), rgba(29, 107, 82, 0.94));
        color: #f8f4ec;
        border-radius: 28px;
        padding: 36px;
        box-shadow: var(--shadow);
        overflow: hidden;
        position: relative;
      }

      .hero > * {
        position: relative;
        z-index: 1;
      }

      .hero::after {
        content: "";
        position: absolute;
        inset: auto -80px -100px auto;
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: rgba(198, 90, 24, 0.22);
        filter: blur(6px);
        z-index: 0;
      }

      .eyebrow {
        display: inline-block;
        padding: 6px 12px;
        border: 1px solid rgba(248, 244, 236, 0.28);
        border-radius: 999px;
        font-size: 12px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
      }

      h1,
      h2,
      h3 {
        margin: 0;
        line-height: 1.05;
      }

      h1 {
        font-size: clamp(42px, 7vw, 78px);
        margin-top: 16px;
        max-width: 700px;
      }

      .dek {
        margin-top: 18px;
        max-width: 760px;
        font-size: 20px;
        line-height: 1.5;
        color: rgba(248, 244, 236, 0.88);
      }

      .hero-meta {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-top: 28px;
      }

      .meta-card,
      .card {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow);
      }

      .meta-card {
        padding: 18px;
        color: var(--ink);
      }

      .meta-label {
        display: block;
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 8px;
      }

      .meta-value {
        font-size: 20px;
        font-weight: 700;
      }

      .grid {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 20px;
        margin-top: 22px;
      }

      .card {
        padding: 24px;
      }

      .card h2 {
        font-size: 28px;
        margin-bottom: 16px;
      }

      .card h3 {
        font-size: 18px;
        margin-bottom: 8px;
      }

      p {
        margin: 0 0 14px;
        font-size: 17px;
        line-height: 1.65;
      }

      .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
      }

      .pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 10px 14px;
        font-size: 14px;
        background: rgba(29, 107, 82, 0.06);
      }

      .section-title {
        margin-top: 28px;
        margin-bottom: 14px;
        font-size: 14px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--accent-2);
      }

      .pick-list {
        display: grid;
        gap: 14px;
      }

      .pick {
        padding: 16px 0 0;
        border-top: 1px solid var(--line);
      }

      .pick:first-child {
        padding-top: 0;
        border-top: 0;
      }

      .tag {
        display: inline-block;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 8px;
      }

      ul {
        margin: 0;
        padding-left: 20px;
      }

      li {
        margin-bottom: 10px;
        font-size: 16px;
        line-height: 1.55;
      }

      .two-col {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }

      .archive {
        width: min(1100px, calc(100% - 32px));
        margin: 0 auto;
        padding: 32px 0 56px;
      }

      .archive-list {
        display: grid;
        gap: 16px;
      }

      .archive-item {
        display: block;
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow);
        color: inherit;
        text-decoration: none;
        padding: 22px;
      }

      .archive-item strong {
        display: block;
        font-size: 21px;
        margin-bottom: 8px;
      }

      .archive-meta {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 8px;
      }

      .footer-note {
        margin-top: 22px;
        padding-top: 18px;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 14px;
      }

      @media (max-width: 860px) {
        .grid,
        .two-col {
          grid-template-columns: 1fr;
        }

        .hero {
          padding: 28px;
        }

        h1 {
          font-size: 44px;
        }
      }
"""


def read_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        config = read_json(CONFIG_PATH)
        merged = DEFAULT_CONFIG | config
        return merged
    return dict(DEFAULT_CONFIG)


def render_meta(meta: list[dict[str, str]]) -> str:
    cards = []
    for item in meta:
        cards.append(
            """
          <div class="meta-card">
            <span class="meta-label">{label}</span>
            <span class="meta-value">{value}</span>
          </div>""".format(
                label=escape(item["label"]),
                value=escape(item["value"]),
            )
        )
    return "\n".join(cards)


def render_bullets(items: list[str]) -> str:
    return "<ul>\n" + "\n".join(f"  <li>{item}</li>" for item in items) + "\n</ul>"


def render_pick_list(items: list[dict[str, str]]) -> str:
    rows = []
    for item in items:
        rows.append(
            """
          <div class="pick">
            <span class="tag">{tag}</span>
            <p>{body}</p>
          </div>""".format(
                tag=escape(item["tag"]),
                body=item["body"],
            )
        )
    return '<div class="pick-list">\n' + "\n".join(rows) + "\n        </div>"


def render_rich_text_card(card: dict[str, Any], wrapper: str) -> str:
    parts = [f'        <{wrapper} class="card">', f"          <h2>{escape(card['title'])}</h2>"]
    for text in card.get("paragraphs", []):
        parts.append(f"          <p>{text}</p>")
    pills = card.get("pills", [])
    if pills:
        parts.append('          <div class="pill-row">')
        for pill in pills:
            parts.append(f'            <span class="pill">{escape(pill)}</span>')
        parts.append("          </div>")
    if card.get("subtitle"):
        parts.append(f'          <div class="section-title">{escape(card["subtitle"])}</div>')
    bullets = card.get("bullets", [])
    if bullets:
        parts.append("          " + render_bullets(bullets).replace("\n", "\n          ").rstrip())
    parts.append(f"        </{wrapper}>")
    return "\n".join(parts)


def render_pick_list_card(card: dict[str, Any], wrapper: str) -> str:
    return "\n".join(
        [
            f"        <{wrapper} class=\"card\">",
            f"          <h2>{escape(card['title'])}</h2>",
            "          " + render_pick_list(card["items"]).replace("\n", "\n          ").rstrip(),
            f"        </{wrapper}>",
        ]
    )


def render_grid(block: dict[str, Any]) -> str:
    cards = []
    for index, card in enumerate(block["cards"]):
        wrapper = "article" if index == 0 else "aside"
        kind = card["kind"]
        if kind == "rich-text":
            cards.append(render_rich_text_card(card, wrapper))
        elif kind == "pick-list":
            cards.append(render_pick_list_card(card, wrapper))
        else:
            raise ValueError(f"Unsupported card kind: {kind}")
    return '<section class="grid">\n' + "\n".join(cards) + "\n      </section>"


def render_two_col_list(block: dict[str, Any]) -> str:
    columns = []
    for column in block["columns"]:
        parts = [f"          <div>", f"            <h3>{escape(column['heading'])}</h3>"]
        parts.append(f"            <p>{column['body']}</p>")
        parts.append("            " + render_bullets(column["bullets"]).replace("\n", "\n            ").rstrip())
        parts.append("          </div>")
        columns.append("\n".join(parts))

    return "\n".join(
        [
            '      <section class="card" style="margin-top: 22px;">',
            f"        <h2>{escape(block['title'])}</h2>",
            '        <div class="two-col">',
            "\n".join(columns),
            "        </div>",
            "      </section>",
        ]
    )


def render_block(block: dict[str, Any]) -> str:
    block_type = block["type"]
    if block_type == "grid":
        return render_grid(block)
    if block_type == "two-col-list":
        return render_two_col_list(block)
    raise ValueError(f"Unsupported block type: {block_type}")


def render_embed_resizer(slug: str) -> str:
    safe_slug = json.dumps(slug)
    return f"""\
    <script>
      (function () {{
        var slug = {safe_slug};
        function sendHeight() {{
          if (window.parent === window) return;
          var height = Math.max(
            document.body ? document.body.scrollHeight : 0,
            document.documentElement ? document.documentElement.scrollHeight : 0
          );
          window.parent.postMessage({{ type: "ta-fantasy-height", slug: slug, height: height }}, "*");
        }}
        if ("ResizeObserver" in window) {{
          var observer = new ResizeObserver(sendHeight);
          observer.observe(document.body);
        }}
        window.addEventListener("load", sendHeight);
        window.addEventListener("resize", sendHeight);
        setTimeout(sendHeight, 150);
        setTimeout(sendHeight, 600);
      }})();
    </script>"""


def render_squarespace_embed(config: dict[str, Any]) -> str:
    manifest_url = absolute_url(config["public_base_url"], "/manifest/latest.json")
    return f"""\
<div id="ta-fantasy-cheat-sheet" style="width:100%;">
  <p>Loading the latest ATP Fantasy cheat sheet...</p>
</div>
<script>
  (function () {{
    var manifestUrl = "{escape(manifest_url, quote=True)}";
    var mount = document.getElementById("ta-fantasy-cheat-sheet");
    var iframe;

    function setFallback(message, url) {{
      var html = "<p>" + message + "</p>";
      if (url) {{
        html += '<p><a href="' + url + '" target="_blank" rel="noopener">Open the cheat sheet in a new tab</a></p>';
      }}
      mount.innerHTML = html;
    }}

    fetch(manifestUrl, {{ cache: "no-store" }})
      .then(function (response) {{
        if (!response.ok) throw new Error("Manifest request failed");
        return response.json();
      }})
      .then(function (manifest) {{
        if (!manifest.current || !manifest.current.url) throw new Error("Manifest missing current page");

        iframe = document.createElement("iframe");
        iframe.src = manifest.current.url;
        iframe.title = manifest.current.label || "ATP Fantasy Cheat Sheet";
        iframe.style.width = "100%";
        iframe.style.minHeight = "2200px";
        iframe.style.border = "0";
        iframe.style.display = "block";
        iframe.style.background = "transparent";
        iframe.loading = "lazy";

        mount.innerHTML = "";
        mount.appendChild(iframe);
      }})
      .catch(function () {{
        setFallback("The cheat sheet could not be loaded right now.", manifestUrl);
      }});

    window.addEventListener("message", function (event) {{
      if (!iframe || event.source !== iframe.contentWindow) return;
      if (!event.data || event.data.type !== "ta-fantasy-height") return;
      if (typeof event.data.height !== "number") return;
      iframe.style.height = Math.max(1200, event.data.height + 24) + "px";
    }});
  }})();
</script>
"""


def render_page(data: dict[str, Any]) -> str:
    blocks = "\n\n".join(render_block(block) for block in data["blocks"])
    footer = ""
    if data.get("footer_note"):
        footer = f"""
      <section class="card" style="margin-top: 22px;">
        <div class="footer-note">{data["footer_note"]}</div>
      </section>"""
    slug = data["publish"]["filename"].removesuffix(".html")

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(data["page_title"])}</title>
    <style>
{STYLE}
    </style>
  </head>
  <body>
    <main class="wrap">
      <section class="hero">
        <span class="eyebrow">{escape(data["eyebrow"])}</span>
        <h1>{escape(data["headline"])}</h1>
        <p class="dek">{data["dek"]}</p>
        <div class="hero-meta">
{render_meta(data["meta"])}
        </div>
      </section>

{blocks}{footer}
    </main>
{render_embed_resizer(slug)}
  </body>
</html>
"""


def render_archive_index(config: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    items = []
    for page in pages:
        publish = page["publish"]
        url = page["relative_url"]
        items.append(
            """
        <a class="archive-item" href="{url}">
          <div class="archive-meta">{week} | {label}</div>
          <strong>{headline}</strong>
          <p>{description}</p>
        </a>""".format(
                url=escape(url, quote=True),
                week=escape(publish["week"]),
                label=escape(publish["label"]),
                headline=escape(page["headline"]),
                description=page.get("archive_summary", page["dek"]),
            )
        )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(config["site_title"])} | Archive</title>
    <style>
{STYLE}
    </style>
  </head>
  <body>
    <main class="archive">
      <section class="hero">
        <span class="eyebrow">Tennis Automated | ATP Fantasy Archive</span>
        <h1>Published Cheat Sheets</h1>
        <p class="dek">Versioned weekly ATP Fantasy pages live here. Squarespace should always load the current page from the latest manifest, but every published edition remains available in the archive.</p>
      </section>

      <section class="card" style="margin-top: 22px;">
        <h2>Archive</h2>
        <div class="archive-list">
{''.join(items)}
        </div>
      </section>
    </main>
  </body>
</html>
"""


def validate_week_data(data: dict[str, Any], source_path: Path) -> None:
    required_top = ["page_title", "eyebrow", "headline", "dek", "meta", "blocks", "output", "publish"]
    for key in required_top:
        if key not in data:
            raise ValueError(f"{source_path.name}: missing required field '{key}'")

    publish_required = ["filename", "week", "label", "updated_at", "live"]
    for key in publish_required:
        if key not in data["publish"]:
            raise ValueError(f"{source_path.name}: missing publish.{key}")
    if "draft" in data["publish"] and not isinstance(data["publish"]["draft"], bool):
        raise ValueError(f"{source_path.name}: publish.draft must be true or false")


def load_weeks(paths: list[Path]) -> list[dict[str, Any]]:
    pages = []
    for path in paths:
        data = read_json(path)
        validate_week_data(data, path)
        data["_source_path"] = path
        pages.append(data)
    return pages


def is_draft(page: dict[str, Any]) -> bool:
    return bool(page["publish"].get("draft", False))


def ensure_publish_targets(pages: list[dict[str, Any]]) -> None:
    filenames = {}
    live_pages = []
    for page in pages:
        filename = page["publish"]["filename"]
        if filename in filenames:
            raise ValueError(f"Duplicate publish filename: {filename}")
        filenames[filename] = page["_source_path"]
        if is_draft(page):
            if page["publish"]["live"]:
                raise ValueError(f"{page['_source_path'].name}: draft pages cannot have publish.live=true")
            continue
        if page["publish"]["live"]:
            live_pages.append(page)
    if len(live_pages) != 1:
        raise ValueError("Exactly one page must have publish.live=true")


def absolute_url(base_url: str, relative_url: str) -> str:
    return f"{base_url.rstrip('/')}/{relative_url.lstrip('/')}"


def build_pages(pages: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    DIST_DIR.mkdir(exist_ok=True)
    PAGES_DIR.mkdir(exist_ok=True)
    MANIFEST_DIR.mkdir(exist_ok=True)

    built_pages: list[dict[str, Any]] = []
    for page in pages:
        html = render_page(page)
        local_output = BASE_DIR / page["output"]
        local_output.write_text(html)

        dist_output: Path | None = None
        relative_url: str | None = None
        public_url: str | None = None
        if not is_draft(page):
            publish_filename = page["publish"]["filename"]
            dist_output = PAGES_DIR / publish_filename
            dist_output.write_text(html)
            relative_url = f"/pages/{publish_filename}"
            public_url = absolute_url(config["public_base_url"], relative_url)

        built_pages.append(
            {
                **page,
                "local_output": str(local_output),
                "dist_output": str(dist_output) if dist_output else None,
                "relative_url": relative_url,
                "public_url": public_url,
            }
        )
    return built_pages


def build_latest_manifest(config: dict[str, Any], built_pages: list[dict[str, Any]]) -> dict[str, Any]:
    published_pages = [page for page in built_pages if not is_draft(page)]
    current = next(page for page in published_pages if page["publish"]["live"])
    manifest = {
        "site_title": config["site_title"],
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "current": {
            "week": current["publish"]["week"],
            "label": current["publish"]["label"],
            "updated_at": current["publish"]["updated_at"],
            "relative_url": current["relative_url"],
            "url": current["public_url"],
            "source": str(current["_source_path"].relative_to(BASE_DIR)),
        },
    }
    (MANIFEST_DIR / "latest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def build_archive_manifest(built_pages: list[dict[str, Any]]) -> None:
    archive = []
    published_pages = [page for page in built_pages if not is_draft(page)]
    for page in sorted(published_pages, key=lambda item: item["publish"]["updated_at"], reverse=True):
        archive.append(
            {
                "week": page["publish"]["week"],
                "label": page["publish"]["label"],
                "updated_at": page["publish"]["updated_at"],
                "relative_url": page["relative_url"],
                "url": page["public_url"],
                "headline": page["headline"],
                "source": str(page["_source_path"].relative_to(BASE_DIR)),
            }
        )
    (MANIFEST_DIR / "archive.json").write_text(json.dumps({"pages": archive}, indent=2) + "\n")


def build_archive_index(config: dict[str, Any], built_pages: list[dict[str, Any]]) -> None:
    ordered = sorted(
        [page for page in built_pages if not is_draft(page)],
        key=lambda item: item["publish"]["updated_at"],
        reverse=True,
    )
    (DIST_DIR / "index.html").write_text(render_archive_index(config, ordered))


def write_support_files() -> None:
    (DIST_DIR / "_headers").write_text(
        "/manifest/latest.json\n"
        "  Cache-Control: no-store, max-age=0\n"
        "  Access-Control-Allow-Origin: *\n\n"
        "/manifest/archive.json\n"
        "  Cache-Control: no-store, max-age=0\n"
        "  Access-Control-Allow-Origin: *\n\n"
        "/pages/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n\n"
        "/index.html\n"
        "  Cache-Control: public, max-age=300\n"
    )
    config = load_config()
    (BASE_DIR / "squarespace-code-block.html").write_text(render_squarespace_embed(config))


def build_all(paths: list[Path]) -> list[dict[str, Any]]:
    config = load_config()
    pages = load_weeks(paths)
    ensure_publish_targets(pages)
    built_pages = build_pages(pages, config)
    build_latest_manifest(config, built_pages)
    build_archive_manifest(built_pages)
    build_archive_index(config, built_pages)
    write_support_files()
    return built_pages


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        paths = sorted(DATA_DIR.glob("*.json"))
    else:
        paths = [BASE_DIR / arg if not arg.startswith("/") else Path(arg) for arg in argv[1:]]

    if not paths:
        raise SystemExit("No week data files found.")

    built_pages = build_all(paths)
    for page in built_pages:
        print(f"built {page['local_output']}")
        if page["dist_output"]:
            print(f"published {page['dist_output']}")
    print(f"wrote {MANIFEST_DIR / 'latest.json'}")
    print(f"wrote {DIST_DIR / 'index.html'}")
    print(f"wrote {BASE_DIR / 'squarespace-code-block.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
