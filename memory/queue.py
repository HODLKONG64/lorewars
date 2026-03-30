import json
from pathlib import Path

QUEUE_PATH = Path(__file__).parent / "queue.json"


def _load():
    if not QUEUE_PATH.exists():
        return []
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def push(entry: dict):
    data = _load()
    data.append(entry)
    _save(data)


def pop():
    data = _load()
    if not data:
        return None
    item = data.pop(0)
    _save(data)
    return item


def length():
    return len(_load())


def all():
    return _load()


def clear():
    _save([])