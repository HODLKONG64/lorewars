import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

LEDGERS_DIR = Path(__file__).parent.parent / "memory" / "ledgers"


def publish(log_dict: dict) -> str:
    dry_run = os.environ.get("LOREWARS_DRY_RUN", "true").lower() == "true"

    endpoint = os.environ.get("IPFS_ENDPOINT", "").strip()
    api_key = os.environ.get("IPFS_API_KEY", "").strip()

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    ledger_path = LEDGERS_DIR / f"ledger-{today}.json"
    LEDGERS_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "date": today,
        "slug": log_dict["slug"],
        "source_url": log_dict["metadata"]["source_url"],
        "source_name": log_dict["metadata"]["source_name"],
        "scenario": log_dict["metadata"]["scenario"],
        "tone": log_dict["metadata"]["tone"],
    }

    if dry_run:
        fake_cid = f"Qm{log_dict['slug'].replace('-', '')[:44]}"
        print(f"[ipfs_publisher] DRY RUN — would publish ledger to IPFS. Fake CID: {fake_cid}")
        ledger_record = {**payload, "cid": fake_cid, "dry_run": True}
        ledger_path.write_text(json.dumps(ledger_record, indent=2), encoding="utf-8")
        return fake_cid

    if not endpoint:
        print("[ipfs_publisher] IPFS publish failed: IPFS_ENDPOINT is empty")
        cid = "ERROR"
        ledger_record = {**payload, "cid": cid, "dry_run": False}
        ledger_path.write_text(json.dumps(ledger_record, indent=2), encoding="utf-8")
        return cid

    if not api_key:
        print("[ipfs_publisher] IPFS publish failed: IPFS_API_KEY is empty")
        cid = "ERROR"
        ledger_record = {**payload, "cid": cid, "dry_run": False}
        ledger_path.write_text(json.dumps(ledger_record, indent=2), encoding="utf-8")
        return cid

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    pinata_payload = {
        "pinataContent": payload,
        "pinataMetadata": {
            "name": f"lorewars-ledger-{today}"
        }
    }

    try:
        resp = requests.post(
            endpoint,
            headers=headers,
            json=pinata_payload,
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()
        cid = data.get("IpfsHash") or data.get("Hash") or data.get("cid") or "UNKNOWN"

    except Exception as exc:
        print(f"[ipfs_publisher] IPFS publish failed: {exc}")
        cid = "ERROR"

    ledger_record = {**payload, "cid": cid, "dry_run": False}
    ledger_path.write_text(json.dumps(ledger_record, indent=2), encoding="utf-8")
    print(f"[ipfs_publisher] Published ledger. CID: {cid}")
    return cid