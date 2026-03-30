import json
from pathlib import Path

HISTORY_PATH = Path(__file__).parent / "history.json"


def _load() -> list:
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(history: list) -> None:
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def add_entry(url: str, source_name: str, log_slug: str, date: str) -> None:
    history = _load()
    history.append(
        {"url": url, "source_name": source_name, "log_slug": log_slug, "date": date}
    )
    _save(history)


def has_url(url: str) -> bool:
    history = _load()
    return any(entry["url"] == url for entry in history)


def recent_sources(n: int) -> list:
    history = _load()
    return [entry["source_name"] for entry in history[-n:]]


def all_entries() -> list:
    return _load()
