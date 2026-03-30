from memory import queue, history


def select() -> dict | None:
    queue_items = queue.all()

    if not queue_items:
        all_entries = history.all_entries()
        if all_entries:
            oldest = all_entries[0]
            print(f"[source_selector] Queue empty — reusing oldest history entry: {oldest['url']}")
            return {
                "url": oldest["url"],
                "source_name": oldest.get("source_name", "Unknown"),
                "title": oldest.get("log_slug", ""),
            }
        return None

    # Simple scoring — prioritise longer URLs (proxy for richer content)
    best = max(queue_items, key=lambda x: len(x.get("url", "")))

    # Remove selected item from queue
    queue.remove(best["url"])

    return best