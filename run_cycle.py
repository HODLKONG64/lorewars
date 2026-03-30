#!/usr/bin/env python3
"""
Lorewars Phase 1 — Main Cycle Entrypoint
"""
from dotenv import load_dotenv
load_dotenv()

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crawlers import rss_crawler
from generators import source_selector, log_generator
from publishers import wiki_publisher, ipfs_publisher, search_index
from memory import queue, history

WORLD_STATE_PATH = Path(__file__).parent / "memory" / "world_state.json"
ARC_STATE_PATH = Path(__file__).parent / "memory" / "arc_state.json"

DRY_RUN = os.environ.get("LOREWARS_DRY_RUN", "true").lower() == "true"


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _update_world_state(log_dict: dict) -> None:
    state = _load_json(WORLD_STATE_PATH)
    state["run_count"] = state.get("run_count", 0) + 1
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    _save_json(WORLD_STATE_PATH, state)


def _update_arc_state(log_dict: dict) -> None:
    state = _load_json(ARC_STATE_PATH)
    state["logs_in_arc"] = state.get("logs_in_arc", 0) + 1
    if state.get("started") is None:
        state["started"] = datetime.now(timezone.utc).isoformat()
    _save_json(ARC_STATE_PATH, state)


def main() -> None:
    print("=" * 60)
    print("LOREWARS CYCLE START")
    print(f"DRY_RUN={DRY_RUN}")
    print("=" * 60)

    print("\n[1/7] Crawling RSS and archive sources...")
    new_urls = rss_crawler.run()
    print(f"      Queue length: {queue.length()}")

    print("\n[2/7] Selecting source URL...")
    source_entry = source_selector.select()
    if source_entry is None:
        print("      No source available — aborting cycle.")
        return
    print(f"      Selected: {source_entry['url']}")

    print("\n[3/7] Generating war log...")
    log_dict = log_generator.generate(source_entry)
    print(f"      Slug: {log_dict['slug']}")

    print("\n[4/7] Publishing wiki page...")
    log_path = wiki_publisher.publish(log_dict)
    print(f"      Written: {log_path}")

    print("\n[5/7] Publishing to IPFS...")
    cid = ipfs_publisher.publish(log_dict)
    print(f"      CID: {cid}")

    print("\n[6/7] Building search index...")
    search_index.build()

    print("\n[7/7] Updating memory state...")
    history.add_entry(
        url=source_entry["url"],
        source_name=source_entry["source_name"],
        log_slug=log_dict["slug"],
        date=log_dict["metadata"]["date"],
    )
    _update_world_state(log_dict)
    _update_arc_state(log_dict)

    print("\n" + "=" * 60)
    print("LOREWARS CYCLE COMPLETE")
    print(f"  Log slug  : {log_dict['slug']}")
    print(f"  Source    : {source_entry['source_name']}")
    print(f"  IPFS CID  : {cid}")
    print(f"  New URLs  : {new_urls}")
    print("=" * 60)


if __name__ == "__main__":
    main()
