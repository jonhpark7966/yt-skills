#!/usr/bin/env python3
"""Validate and repair an LLM-proposed chapter list against YouTube's rules.

YouTube chapter requirements (https://support.google.com/youtube/answer/9884579):
  - the first chapter MUST start at 00:00,
  - at least 3 chapters,
  - timestamps in ascending order,
  - each chapter at least 10 seconds long.

This script is the deterministic gate after the model proposes boundaries from
(possibly several) transcript chunks. It snaps/sorts/dedupes, enforces the
10-second minimum, guarantees a 00:00 start, and formats the YouTube block.

Input: JSON array on stdin or via --file:
  [{"time": "MM:SS" | "H:MM:SS" | <seconds>, "title": "..."}, ...]

Output (stdout): JSON
  {"ok": bool, "chapters": [{"time": "MM:SS", "seconds": int, "title": "..."}],
   "youtube_block": "00:00 Intro\n01:35 ...", "warnings": [...], "errors": [...]}
Exit code 0 if ok, 3 if it cannot satisfy the rules (caller must re-segment).

Stdlib only.
"""
import argparse
import json
import re
import sys

MIN_CHAPTERS = 3
MIN_GAP_S = 10
TITLE_SOFT_MAX = 50   # display sweet spot
TITLE_HARD_MAX = 100  # YouTube cap


def to_seconds(val):
    if isinstance(val, (int, float)):
        return int(round(val))
    s = str(val).strip()
    m = re.match(r"^(?:(\d+):)?(\d{1,2}):(\d{2})$", s)
    if m:
        h = int(m.group(1)) if m.group(1) else 0
        return h * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    if s.isdigit():
        return int(s)
    raise ValueError(f"unparseable time: {val!r}")


def fmt(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def process(raw_chapters, duration_s=None):
    warnings, errors = [], []
    parsed = []
    for ch in raw_chapters:
        try:
            secs = to_seconds(ch.get("time"))
        except (ValueError, AttributeError) as e:
            errors.append(str(e))
            continue
        title = str(ch.get("title", "")).strip()
        if not title:
            warnings.append(f"empty title at {fmt(secs)} — skipped")
            continue
        parsed.append({"seconds": secs, "title": title})

    parsed.sort(key=lambda c: c["seconds"])

    # Snap the earliest chapter to 00:00 (YouTube requires it).
    if parsed and parsed[0]["seconds"] != 0:
        warnings.append(f"first chapter was at {fmt(parsed[0]['seconds'])}; snapped to 00:00")
        parsed[0]["seconds"] = 0

    # Enforce ascending order with a >=10s gap; drop offenders (keep the earlier).
    kept = []
    for ch in parsed:
        if kept and ch["seconds"] - kept[-1]["seconds"] < MIN_GAP_S:
            warnings.append(f"dropped '{ch['title']}' at {fmt(ch['seconds'])} (<{MIN_GAP_S}s after previous)")
            continue
        kept.append(ch)

    # Title length checks.
    for ch in kept:
        if len(ch["title"]) > TITLE_HARD_MAX:
            ch["title"] = ch["title"][:TITLE_HARD_MAX].rstrip()
            warnings.append(f"title truncated to {TITLE_HARD_MAX} chars: '{ch['title']}'")
        elif len(ch["title"]) > TITLE_SOFT_MAX:
            warnings.append(f"title >{TITLE_SOFT_MAX} chars (may truncate on mobile): '{ch['title']}'")

    if duration_s is not None:
        kept = [c for c in kept if c["seconds"] < duration_s]

    if len(kept) < MIN_CHAPTERS:
        errors.append(
            f"only {len(kept)} valid chapter(s); YouTube needs >={MIN_CHAPTERS}. "
            "Re-segment with finer boundaries."
        )

    chapters = [{"time": fmt(c["seconds"]), "seconds": c["seconds"], "title": c["title"]} for c in kept]
    block = "\n".join(f"{c['time']} {c['title']}" for c in chapters)
    return {
        "ok": not errors,
        "chapters": chapters,
        "youtube_block": block,
        "warnings": warnings,
        "errors": errors,
    }


def main():
    ap = argparse.ArgumentParser(description="Validate/repair chapters against YouTube rules.")
    ap.add_argument("--file", help="JSON file (default: read stdin)")
    ap.add_argument("--duration-seconds", type=float, default=None, help="Total video duration (drops out-of-range chapters)")
    args = ap.parse_args()

    src = open(args.file, encoding="utf-8") if args.file else sys.stdin
    try:
        data = json.load(src)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "errors": [f"invalid JSON: {e}"]}), file=sys.stderr)
        sys.exit(3)
    finally:
        if args.file:
            src.close()

    if isinstance(data, dict) and "chapters" in data:
        data = data["chapters"]
    if not isinstance(data, list):
        print(json.dumps({"ok": False, "errors": ["expected a JSON array of {time,title}"]}), file=sys.stderr)
        sys.exit(3)

    result = process(data, args.duration_seconds)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    sys.exit(0 if result["ok"] else 3)


if __name__ == "__main__":
    main()
