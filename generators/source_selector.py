"""
Source selector for Lorewars.

Selects the next URL to process.
Now prioritises higher-signal entries instead of pure FIFO.
"""

from memory import queue, history


def select() -> dict | None:
    """
    Select the next source entry.

    Priority:
    1. Highest-signal item from queue (based on URL length heuristic)
    2. Fallback to oldest history entry if queue is empty
    """

    # 🔥 PRIORITY: BEST ITEM FROM QUEUE (NOT RANDOM / NOT FIFO)
    if queue.length() > 0:
        items = queue.all()

        if items:
            best = max(items, key=lambda x: len(x.get("url", "")))
            queue.remove(best["url"])  # prevent reuse
            return best

    # 🧠 FALLBACK: REUSE OLDEST HISTORY ENTRY
    all_entries = history.all_entries()
    if all_entries:
        oldest = all_entries[0]
        print(f"[source_selector] Queue empty — reusing oldest history entry: {oldest['url']}")

        return {
            "url": oldest["url"],
            "source_name": oldest["source_name"],
            "title": oldest.get("log_slug", ""),
        }

    # ❌ NOTHING AVAILABLE
    return None