import random
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

SCENARIOS = [
    "Alfie intercepts a coded transmission from a rival crew",
    "Alfie decrypts a ledger entry hidden in plain sight on the blockchain",
    "Alfie tracks a ghost wallet moving $BLAZE across encrypted bridges",
    "Alfie drops a war log after a midnight spray run on the digital wall",
    "Alfie uncovers a defector passing intelligence to the establishment",
]

TONES = [
    "gritty street dispatch",
    "encrypted broadcast",
    "late-night war room briefing",
    "raw graffiti communiqué",
    "underground intelligence bulletin",
]

ARTICLE_FETCH_LIMIT = 4000


def _fetch_article_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "LorewarsBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        article = soup.find("article") or soup.find("main") or soup.body
        if article:
            return article.get_text(separator=" ", strip=True)[:ARTICLE_FETCH_LIMIT]
    except Exception as exc:
        print(f"[log_generator] Failed to fetch article content: {exc}")
    return ""


def _build_narrative(article_text: str, scenario: str, tone: str, source_name: str) -> str:
    preview = article_text[:600].strip() if article_text else "[signal lost — no data recovered]"

    narrative = f"""\
The city doesn't sleep and neither does Alfie "The Bitcoin KID" Blaze.

This drop comes straight from the intel loop — source locked, frequency verified, threat level elevated.

**Scenario:** {scenario}

Alfie clocked the signal first. While the normies were still trusting the feed, the crew already had the coordinates. The evidence wall doesn't lie. Every block, every hash, every entry in the ledger tells a story — and right now that story has $BLAZE at the centre of a play nobody saw coming.

---

**RAW INTERCEPT — SOURCE: {source_name.upper()}**

{preview}

---

The intelligence checks out. Cross-referenced against three prior logs, zero anomalies in the chain of custody. The $BLAZE token keeps moving — not because it's noise, but because it's signal. Every run confirms it.

Alfie doesn't speculate. Alfie documents. The war log is the proof, the wiki is the wall, and the ledger is the permanent record.

Stay locked.

*— A. Blaze // Lorewars Field Log*
"""
    return narrative.strip()


def generate(source_entry: dict) -> dict:
    url = source_entry["url"]
    source_name = source_entry.get("source_name", "Unknown")

    now = datetime.now(timezone.utc)
    slug = f"LOG-{now.strftime('%Y%m%d-%H%M%S')}"

    scenario = random.choice(SCENARIOS)
    tone = random.choice(TONES)
    article_text = _fetch_article_text(url)

    narrative = _build_narrative(article_text, scenario, tone, source_name)

    frontmatter = (
        f"---\n"
        f"date: {now.isoformat()}\n"
        f"source_url: {url}\n"
        f"source_name: {source_name}\n"
        f"scenario: \"{scenario}\"\n"
        f"tone: \"{tone}\"\n"
        f"anomaly_state: nominal\n"
        f"---\n"
    )

    markdown_content = f"{frontmatter}\n# {slug}\n\n{narrative}\n"

    return {
        "slug": slug,
        "title": slug,
        "markdown_content": markdown_content,
        "metadata": {
            "date": now.isoformat(),
            "source_url": url,
            "source_name": source_name,
            "scenario": scenario,
            "tone": tone,
            "anomaly_state": "nominal",
        },
    }
