"""
Source selector with tiered signal scoring.
"""

from memory import queue, history


KEYWORDS = [
    "bitcoin", "crypto", "blockchain", "nft", "token",
    "ai", "agent", "war", "attack", "hack",
    "finance", "economy", "market", "trading",
]

SOURCE_WEIGHTS = {
    "substack": 40,
    "medium": 25,
    "paragraph": 25,
    "mirror": 20,
    "coindesk": 20,
    "cointelegraph": 20,
    "decrypt": 18,
    "bitcoin.com": 18,
    "theblock": 18,
    "bankless": 18,
}


def _score(entry: dict) -> int:
    url = entry.get("url", "").lower()
    source_name = entry.get("source_name", "").lower()
    score = 0

    # source weighting
    for source_key, weight in SOURCE_WEIGHTS.items():
        if source_key in url or source_key in source_name:
            score += weight

    # keyword weighting
    for keyword in KEYWORDS:
        if keyword in url:
            score += 10

    # slight depth bonus
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