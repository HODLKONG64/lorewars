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
PREVIEW_LIMIT = 600

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/",
}


def _clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _fetch_article_text(url: str) -> str:
    try:
        with requests.Session() as session:
            session.headers.update(REQUEST_HEADERS)
            resp = session.get(url, timeout=20, allow_redirects=True)

            if resp.status_code == 403:
                resp = session.get(f"https://textise.net/showtext.aspx?strURL={url}", timeout=20)

            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            for tag in soup(["script","style","nav","header","footer","aside","noscript"]):
                tag.decompose()

            article = soup.find("article") or soup.find("main") or soup.body

            if article:
                text = _clean_text(article.get_text(" ", strip=True))
                if text:
                    print("[log_generator] SUCCESS FETCH")
                    return text[:ARTICLE_FETCH_LIMIT]

    except Exception as exc:
        print(f"[log_generator] FAIL: {exc}")

    return ""

def _build_preview(article_text: str, source_name: str) -> str:
    if article_text:
        return article_text[:PREVIEW_LIMIT].strip()

    return (
        f"[signal partially blocked — full article body could not be recovered from {source_name}; "
        f"source was still detected, logged, and archived for the evidence wall]"
    )


def _build_narrative(article_text: str, scenario: str, tone: str, source_name: str) -> str:
    preview = _build_preview(article_text, source_name)

    narrative = f"""\
The city doesn't sleep and neither does Alfie "The Bitcoin KID" Blaze.

This drop comes straight from the intel loop — source locked, frequency verified, threat level elevated.

**Scenario:** {scenario}  
**Tone:** {tone}

Alfie clocked the signal first. While the normies were still trusting the feed, the crew already had the coordinates.
The evidence wall doesn't lie. Every block, every hash, every entry in the ledger tells a story — and right now
that story has $BLAZE at the centre of a play nobody saw coming.

---

**RAW INTERCEPT — SOURCE: {source_name.upper()}**

{preview}

---

The intelligence checks out. Cross-referenced against prior logs, then pushed to the wall.
The $BLAZE signal keeps moving — not because it's noise, but because it's signal.
Every run confirms it. Every log leaves a mark.

Alfie doesn't speculate. Alfie documents.

The war log is the proof.  
The wiki is the wall.  
The ledger is the permanent record.

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