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
    print("=" * 60, flush=True)
    print("LOREWARS CYCLE START", flush=True)
    print(f"DRY_RUN={DRY_RUN}", flush=True)
    print("=" * 60, flush=True)

    print("[DEBUG] starting rss_crawler.run()", flush=True)
    new_urls = rss_crawler.run()
    print(f"[DEBUG] new_urls={new_urls}", flush=True)
    print(f"[DEBUG] queue length={queue.length()}", flush=True)

    print("[DEBUG] starting source_selector.select()", flush=True)
    source_entry = source_selector.select()
    print(f"[DEBUG] source_entry={source_entry}", flush=True)

    if source_entry is None:
        print("[DEBUG] No source available — aborting cycle.", flush=True)
        return

    print("[DEBUG] starting log_generator.generate()", flush=True)
    log_dict = log_generator.generate(source_entry)
    print(f"[DEBUG] log_dict={log_dict}", flush=True)

    if not log_dict:
        print("[DEBUG] Skipped — weak content", flush=True)
        return

    print("[DEBUG] starting wiki_publisher.publish()", flush=True)
    log_path = wiki_publisher.publish(log_dict)
    print(f"[DEBUG] log_path={log_path}", flush=True)

    print("[DEBUG] starting ipfs_publisher.publish()", flush=True)
    cid = ipfs_publisher.publish(log_dict)
    print(f"[DEBUG] cid={cid}", flush=True)

    print("[DEBUG] starting search_index.build()", flush=True)
    search_index.build()
    print("[DEBUG] search index built", flush=True)

    print("[DEBUG] starting history.add_entry()", flush=True)
    history.add_entry(
        url=source_entry["url"],
        source_name=source_entry["source_name"],
        log_slug=log_dict["slug"],
        date=log_dict["metadata"]["date"],
    )
    print("[DEBUG] history updated", flush=True)

    print("[DEBUG] starting _update_world_state()", flush=True)
    _update_world_state(log_dict)
    print("[DEBUG] world state updated", flush=True)

    print("[DEBUG] starting _update_arc_state()", flush=True)
    _update_arc_state(log_dict)
    print("[DEBUG] arc state updated", flush=True)

    print("=" * 60, flush=True)
    print("LOREWARS CYCLE COMPLETE", flush=True)
    print(f"  Log slug  : {log_dict['slug']}", flush=True)
    print(f"  Source    : {source_entry['source_name']}", flush=True)
    print(f"  IPFS CID  : {cid}", flush=True)
    print(f"  New URLs  : {new_urls}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()