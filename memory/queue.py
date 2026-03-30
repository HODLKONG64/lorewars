import json
import os
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "queue.json"


def load() -> list:
    if QUEUE_PATH.exists():
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save(queue: list) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


def push(url: str, source_name: str, title: str) -> None:
    queue = load()
    urls = {item["url"] for item in queue}
    if url not in urls:
        queue.append({"url": url, "source_name": source_name, "title": title})
        save(queue)


def pop() -> dict | None:
    queue = load()
    if not queue:
        return None
    item = queue.pop(0)
    save(queue)
    return item


def peek() -> dict | None:
    queue = load()
    return queue[0] if queue else None


def length() -> int:
    return len(load())
