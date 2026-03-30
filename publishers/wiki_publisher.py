from pathlib import Path

WIKI_LOGS_DIR = Path(__file__).parent.parent / "wiki" / "logs"
WIKI_INDEX_PATH = Path(__file__).parent.parent / "wiki" / "index.md"
WIKI_README_PATH = Path(__file__).parent.parent / "wiki" / "README.md"


def _ensure_dirs() -> None:
    WIKI_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = WIKI_LOGS_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


def _update_index(log_dict: dict) -> None:
    slug = log_dict["slug"]
    date = log_dict["metadata"]["date"][:10]
    source_name = log_dict["metadata"]["source_name"]
    link_line = f"- [{slug}](logs/{slug}.md) — {date} — {source_name}\n"

    if not WIKI_INDEX_PATH.exists():
        content = "# Lorewars Log Archive\n\nRunning archive of all Alfie war logs.\n\n<!-- logs will be appended below -->\n"
        WIKI_INDEX_PATH.write_text(content, encoding="utf-8")

    raw = WIKI_INDEX_PATH.read_text(encoding="utf-8")
    marker = "<!-- logs will be appended below -->"
    if marker in raw:
        raw = raw.replace(marker, f"{marker}\n{link_line}")
    else:
        raw += link_line
    WIKI_INDEX_PATH.write_text(raw, encoding="utf-8")


def _update_readme(log_dict: dict) -> None:
    if WIKI_README_PATH.exists():
        return
    content = (
        "# Lorewars — Evidence Wall\n\n"
        "This is Alfie \"The Bitcoin KID\" Blaze's intelligence hub.\n\n"
        "Every page here is a verified log entry from the field. "
        "The wall doesn't speculate — it documents.\n\n"
        "- [Full Log Archive](index.md)\n"
        "- [Search Index](search_index.json)\n\n"
        "*Stay locked.*\n"
    )
    WIKI_README_PATH.write_text(content, encoding="utf-8")


def publish(log_dict: dict) -> Path:
    _ensure_dirs()

    slug = log_dict["slug"]
    log_path = WIKI_LOGS_DIR / f"{slug}.md"
    log_path.write_text(log_dict["markdown_content"], encoding="utf-8")
    print(f"[wiki_publisher] Wrote {log_path}")

    _update_index(log_dict)
    _update_readme(log_dict)

    return log_path
