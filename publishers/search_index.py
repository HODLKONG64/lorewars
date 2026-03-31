import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

WIKI_LOGS_DIR = Path(__file__).parent.parent / "wiki" / "logs"
SEARCH_INDEX_PATH = Path(__file__).parent.parent / "wiki" / "search_index.json"
LOGS_INDEX_PATH = Path(__file__).parent.parent / "wiki" / "logs-index.json"
SITEMAP_PATH = Path(__file__).parent.parent / "wiki" / "sitemap.xml"


def _parse_frontmatter(text: str) -> dict:
    meta = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            block = text[3:end].strip()
            for line in block.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"')
    return meta


def _extract_preview(text: str, max_chars: int = 200) -> str:
    lines = text.splitlines()
    body_lines = []
    in_frontmatter = False
    fm_count = 0
    for line in lines:
        if line.strip() == "---":
            fm_count += 1
            in_frontmatter = fm_count < 2
            continue
        if in_frontmatter:
            continue
        if line.startswith("#"):
            continue
        stripped = line.strip()
        if stripped:
            body_lines.append(stripped)
        if len(" ".join(body_lines)) >= max_chars:
            break
    preview = " ".join(body_lines)
    return preview[:max_chars] + ("…" if len(preview) > max_chars else "")


def build() -> None:
    base_url = os.environ.get("LOREWARS_BASE_URL", "https://hodlkong64.github.io/lorewars").rstrip("/")

    entries = []
    log_files = sorted(WIKI_LOGS_DIR.glob("LOG-*.md"))

    for log_file in log_files:
        text = log_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        slug = log_file.stem
        date = meta.get("date", "")[:10]
        preview = _extract_preview(text)
        url = f"{base_url}/wiki/logs/{slug}.html"
        entries.append(
            {"slug": slug, "title": slug, "date": date, "preview": preview, "url": url}
        )

    SEARCH_INDEX_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"[search_index] Wrote {len(entries)} entries to {SEARCH_INDEX_PATH}")

    # logs-index.json — lightweight ordered list for the wiki nav
    logs_index = [{"slug": e["slug"], "date": e["date"], "url": e["url"]} for e in entries]
    LOGS_INDEX_PATH.write_text(json.dumps(logs_index, indent=2), encoding="utf-8")
    print(f"[search_index] Wrote {len(logs_index)} entries to {LOGS_INDEX_PATH}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urlset = "\n".join(
        f"  <url>\n    <loc>{e['url']}</loc>\n    <lastmod>{e['date'] or now}</lastmod>\n  </url>"
        for e in entries
    )
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urlset}\n"
        "</urlset>\n"
    )
    SITEMAP_PATH.write_text(sitemap_xml, encoding="utf-8")
    print(f"[search_index] Wrote sitemap to {SITEMAP_PATH}")
