from memory import queue, history

COOLDOWN_RUNS = 3


def select() -> dict | None:
    recent = history.recent_sources(COOLDOWN_RUNS)
    q_length = queue.length()

    for _ in range(q_length):
        candidate = queue.pop()
        if candidate is None:
            break
        if candidate["source_name"] not in recent:
            return candidate
        queue.push(candidate["url"], candidate["source_name"], candidate["title"])

    if queue.length() > 0:
        return queue.pop()

    all_entries = history.all_entries()
    if all_entries:
        oldest = all_entries[0]
        print(f"[source_selector] Queue empty — reusing oldest history entry: {oldest['url']}")
        return {
            "url": oldest["url"],
            "source_name": oldest["source_name"],
            "title": oldest.get("log_slug", ""),
        }

    return None
