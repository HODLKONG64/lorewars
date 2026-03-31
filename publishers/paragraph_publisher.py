"""
Paragraph publisher for Lorewars Phase 1.

Publishes a deeper version of the log to a Paragraph publication.
Stores the published URL in memory/publish_history.json.

Dry-run / missing credentials: records a stub entry so memory is always updated.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

PUBLISH_HISTORY_PATH = Path(__file__).parent.parent / "memory" / "publish_history.json"

# ── Deeper content builder ────────────────────────────────────────────────────

def _build_deeper_content(log_dict: dict) -> str:
    metadata = log_dict.get("metadata", {})
    slug = log_dict["slug"]
    scenario = metadata.get("scenario", "")
    tone = metadata.get("tone", "")
    source_name = metadata.get("source_name", "Unknown")
    source_url = metadata.get("source_url", "")
    anomaly_state = metadata.get("anomaly_state", "nominal")
    date = metadata.get("date", "")[:10]

    raw_markdown = log_dict.get("markdown_content", "")
    body = raw_markdown.split("---")[-1].strip() if "---" in raw_markdown else raw_markdown

    content = f"""\
# {slug} — Extended Field Report

*Published: {date} | Lorewars Intelligence Network*

---

## MISSION BRIEF

Alfie "The Bitcoin KID" Blaze has filed the following extended field report from the intelligence loop.

**Scenario:** {scenario}
**Broadcast Tone:** {tone}
**Anomaly State:** {anomaly_state}
**Primary Source:** [{source_name}]({source_url})

---

## FULL LOG

{body}

---

## INTELLIGENCE NOTES

This log is part of the Lorewars Genesis Arc — Alfie's ongoing documentation of the encrypted city.

Every log is cross-referenced against the evidence wall at the Lorewars wiki.
Every source is verified. Every entry is permanent.

The $BLAZE signal doesn't sleep.

---

*Lorewars is an autonomous narrative system. This report was generated and published without human intervention.*
*Log ID: {slug}*
"""
    return content.strip()


# ── Publish history helpers ───────────────────────────────────────────────────

def _load_history() -> list:
    if PUBLISH_HISTORY_PATH.exists():
        with open(PUBLISH_HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_history(history: list) -> None:
    with open(PUBLISH_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def _record(slug: str, url: str, dry_run: bool) -> None:
    history = _load_history()
    history.append(
        {
            "slug": slug,
            "url": url,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
        }
    )
    _save_history(history)


# ── Public API ────────────────────────────────────────────────────────────────

def publish(log_dict: dict) -> str:
    """
    Publish a deeper version of the log to Paragraph.

    Returns the published URL (or a stub URL in dry-run / error cases).
    Always updates publish_history.json.
    """
    slug = log_dict["slug"]
    api_key = os.environ.get("PARAGRAPH_API_KEY", "").strip()
    publication_id = os.environ.get("PARAGRAPH_PUBLICATION_ID", "").strip()
    dry_run = os.environ.get("LOREWARS_DRY_RUN", "true").lower() == "true"

    if dry_run or not api_key or not publication_id:
        mode = "DRY RUN" if dry_run else "MISSING CREDENTIALS"
        stub_url = f"https://paragraph.xyz/@lorewars/{slug.lower()}"
        print(f"[paragraph_publisher] {mode} — stub URL: {stub_url}")
        _record(slug, stub_url, dry_run=True)
        return stub_url

    title = log_dict.get("title", slug)
    markdown = log_dict.get("markdown_content", "")
    deeper_content = _build_deeper_content(log_dict)

    payload = {
        "title": title,
        "body": deeper_content,
        "status": "published",
    }

    try:
        resp = requests.post(
            f"https://api.paragraph.xyz/blogs/{publication_id}/posts",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        published_url = (
            data.get("url")
            or data.get("link")
            or data.get("post", {}).get("url")
            or f"https://paragraph.xyz/@lorewars/{slug.lower()}"
        )

        print(f"[paragraph_publisher] Published: {published_url}")
        _record(slug, published_url, dry_run=False)
        return published_url

    except Exception as exc:
        print(f"[paragraph_publisher] Publish failed ({exc}) — recording error")
        error_url = f"https://paragraph.xyz/@lorewars/{slug.lower()}"
        _record(slug, error_url, dry_run=False)
        return error_url
