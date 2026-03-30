import json
import os
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

from memory import queue, history

CONFIG_PATH = Path(__file__).parent.parent / "config" / "sources.json"
CRAWL_STATE_PATH = Path(__file__).parent.parent / "memory" / "crawl_state.json"


def _load_sources() -> list:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data["sources"] if s.get("enabled")]


def _load_crawl_state() -> dict:
    if CRAWL_STATE_PATH.exists():
        with open(CRAWL_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_crawl_state(state: dict) -> None:
    with open(CRAWL_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _fetch_rss(source: dict) -> list:
    entries = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            url = entry.get("link", "")
            title = entry.get("title", "")
            if url:
                entries.append({"url": url, "title": title, "source_name": source["name"]})
    except Exception as exc:
        print(f"[rss_crawler] RSS fetch error for {source['name']}: {exc}")
    return entries


def _fetch_archive(source: dict) -> list:
    entries = []
    try:
        resp = requests.get(source["url"], timeout=15, headers={"User-Agent": "LorewarsBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http") and href not in (source["url"],):
                title = a.get_text(strip=True) or href
                entries.append({"url": href, "title": title, "source_name": source["name"]})
    except Exception as exc:
        print(f"[rss_crawler] Archive fetch error for {source['name']}: {exc}")
    return entries


def run() -> int:
    sources = _load_sources()
    crawl_state = _load_crawl_state()
    now_iso = datetime.now(timezone.utc).isoformat()
    new_count = 0

    for source in sources:
        source_type = source.get("type", "rss")
        if source_type == "rss":
            entries = _fetch_rss(source)
        elif source_type == "archive":
            entries = _fetch_archive(source)
        else:
            entries = []

        for entry in entries:
            if not history.has_url(entry["url"]):
                queue.push(entry["url"], entry["source_name"], entry["title"])
                new_count += 1

        crawl_state[source["name"]] = now_iso

    _save_crawl_state(crawl_state)
    print(f"[rss_crawler] Added {new_count} new URLs to queue.")
    return new_count
