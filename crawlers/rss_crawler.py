"""
RSS Crawler — reads approved sources from config/sources.json,
tracks per-source crawl timestamps in memory/crawl_state.json,
and pushes only new (unseen) URLs into the queue.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import feedparser

from memory import queue, history

CONFIG_PATH = Path(__file__).parent.parent / "config" / "sources.json"
CRAWL_STATE_PATH = Path(__file__).parent.parent / "memory" / "crawl_state.json"


# ── Crawl state helpers ───────────────────────────────────────────────────────

def _load_crawl_state() -> dict:
    if CRAWL_STATE_PATH.exists():
        with open(CRAWL_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_crawl_state(state: dict) -> None:
    with open(CRAWL_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _load_sources() -> list:
    if not CONFIG_PATH.exists():
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    sources = [s for s in data.get("sources", []) if s.get("enabled", True) and s.get("type") == "rss"]
    sources.sort(key=lambda s: s.get("priority", 0), reverse=True)
    return sources


# ── Known-URL set (queue + history) ──────────────────────────────────────────

def _known_urls() -> set:
    known = set()
    for item in queue.all():
        known.add(item.get("url", ""))
    for entry in history.all_entries():
        known.add(entry.get("url", ""))
    return known


# ── Public API ────────────────────────────────────────────────────────────────

def run() -> int:
    sources = _load_sources()
    crawl_state = _load_crawl_state()
    known = _known_urls()
    now_iso = datetime.now(timezone.utc).isoformat()
    new_urls = 0

    for source in sources:
        feed_url = source["url"]
        source_name = source["name"]

        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            url = entry.get("link", "").strip()
            title = entry.get("title", "")

            if not url or url in known:
                continue

            queue.push({"url": url, "source_name": source_name, "title": title})
            known.add(url)
            new_urls += 1

        crawl_state[source_name] = now_iso

    _save_crawl_state(crawl_state)
    print(f"[rss_crawler] Added {new_urls} new URLs to queue (checked {len(sources)} sources)")
    return new_urls