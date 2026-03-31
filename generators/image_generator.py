"""
Image generator for Lorewars.

Phase 1: Uses OpenAI DALL-E-3 when OPENAI_API_KEY is present.
Dry-run / missing key: writes a placeholder PNG so the pipeline never
produces zero output.
"""

import base64
import os
import struct
import zlib
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "images"

# ── DALL-E prompt components ──────────────────────────────────────────────────

STYLE_MAP = {
    "gritty street dispatch": "gritty urban graffiti art style, dark alleyway, neon spray paint",
    "encrypted broadcast": "glitchy cyberpunk broadcast, VHS scan lines, digital corruption",
    "late-night war room briefing": "dimly lit war room, holographic maps, blue light, smoke",
    "raw graffiti communiqué": "bold street art, vivid spraypaint tags, concrete wall texture",
    "underground intelligence bulletin": "dark underground bunker, encrypted screens, red light",
}

SCENARIO_KEYWORDS = {
    "intercepts a coded transmission": "radio tower, encrypted signal waves, surveillance",
    "decrypts a ledger entry": "blockchain ledger, glowing numbers, cryptographic keys",
    "tracks a ghost wallet": "digital ghost trail, wallet addresses, neon money flow",
    "midnight spray run": "night time, spray cans, urban wall, flashlight beam",
    "defector passing intelligence": "shadowy figure, handoff, classified documents",
}


def _make_prompt(log_dict: dict) -> str:
    metadata = log_dict.get("metadata", {})
    tone = metadata.get("tone", "gritty street dispatch")
    scenario = metadata.get("scenario", "")

    style = STYLE_MAP.get(tone, "dark urban art, digital graffiti")

    scene_kw = ""
    for key, kw in SCENARIO_KEYWORDS.items():
        if key in scenario.lower():
            scene_kw = kw
            break

    prompt = (
        f"Digital illustration of a young Black male graffiti artist known as 'The Bitcoin KID', "
        f"hoodie up, spray can in hand, standing in a futuristic urban environment. "
        f"Style: {style}. "
        f"Scene details: {scene_kw or 'city skyline at night, graffiti walls, blockchain symbols'}. "
        f"Cinematic composition, high contrast, no text overlays. "
        f"Consistent character: athletic build, early 20s, gold chain, custom trainers."
    )
    return prompt


# ── Placeholder PNG generator (no external dependency) ───────────────────────

def _make_placeholder_png(slug: str) -> bytes:
    """Return a minimal valid 16×16 grey PNG as bytes."""
    def _chunk(name: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
        return length + name + data + crc

    # IHDR: 16×16, 8-bit greyscale
    ihdr_data = struct.pack(">IIBBBBB", 16, 16, 8, 0, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)

    # IDAT: 16 rows of filter-byte + 16 grey pixels (value 0x88)
    raw_rows = b"".join(b"\x00" + bytes([0x88] * 16) for _ in range(16))
    compressed = zlib.compress(raw_rows, 9)
    idat = _chunk(b"IDAT", compressed)

    iend = _chunk(b"IEND", b"")

    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


# ── Public API ────────────────────────────────────────────────────────────────

def generate(log_dict: dict) -> Path:
    """
    Generate an image for the given log and save it under assets/images/.

    Returns the Path to the saved image file.
    Raises RuntimeError only if the directory cannot be created.
    Never returns None — always produces a file.
    """
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    slug = log_dict["slug"]
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    dry_run = os.environ.get("LOREWARS_DRY_RUN", "true").lower() == "true"

    image_path = ASSETS_DIR / f"{slug}.png"

    if dry_run or not api_key:
        mode = "DRY RUN" if dry_run else "NO API KEY"
        print(f"[image_generator] {mode} — writing placeholder image: {image_path}")
        image_path.write_bytes(_make_placeholder_png(slug))
        return image_path

    # Live DALL-E generation
    try:
        prompt = _make_prompt(log_dict)
        print(f"[image_generator] Requesting DALL-E-3 image for {slug}")

        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "b64_json",
            },
            timeout=60,
        )
        resp.raise_for_status()

        b64 = resp.json()["data"][0]["b64_json"]
        image_path.write_bytes(base64.b64decode(b64))
        print(f"[image_generator] Saved DALL-E image: {image_path}")
        return image_path

    except Exception as exc:
        print(f"[image_generator] DALL-E failed ({exc}) — falling back to placeholder")
        image_path.write_bytes(_make_placeholder_png(slug))
        return image_path
