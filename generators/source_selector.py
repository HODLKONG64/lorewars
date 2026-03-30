"""
Source selector with real signal scoring.
"""

from memory import queue, history


KEYWORDS = [
    "bitcoin", "crypto", "blockchain", "nft", "token",
    "ai", "agent", "war", "attack", "hack",
    "finance", "economy", "market", "trading",
]


def _score(entry: dict) -> int:
    url = entry.get("url", "").lower()
    score = 0

    # 🔥 keyword scoring
    for k in KEYWORDS:
        if k in url:
            score += 10

    # 🔥 depth scoring (longer URLs still matter slightly)
    score += len(url) // 10

    return score


def select() -> dict | None:
    if queue.length() > 0:
        items = queue.all()

        if items:
            best = max(items, key=_score)
            queue.remove(best["url"])
            print(f"[source_selector] Selected (score={_score(best)}): {best['url']}")
            return best

    all_entries = history.all_entries()
    if all_entries:
        oldest = all_entries[0]
        print(f"[source_selector] Fallback: {oldest['url']}")

        return {
            "url": oldest["url"],
            "source_name": oldest["source_name"],
            "title": oldest.get("log_slug", ""),
        }

    return None