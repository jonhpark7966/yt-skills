#!/usr/bin/env python3
"""Parse an SRT file and split it into overlapping windows for LLM chaptering.

Long transcripts blow past a single context window, so we cut the SRT into
time-based windows with a small overlap (so a topic boundary sitting near a
chunk edge is still visible in the neighbouring chunk) and emit each window as
timestamped lines the model can read directly.

Output: JSON on stdout.
  {
    "total_duration_s": float,
    "total_duration_hms": "H:MM:SS",
    "cue_count": int,
    "chunk_count": int,
    "chunks": [
      {"chunk_id": 0, "start_s": 0.0, "end_s": 612.0,
       "text": "[00:00] line one\n[00:04] line two\n..."},
      ...
    ]
  }

Stdlib only. Usage:
  python srt_chunk.py transcript.srt
  python srt_chunk.py transcript.srt --window-seconds 600 --overlap-seconds 60
"""
import argparse
import json
import re
import sys

# Accept SRT (HH:MM:SS,mmm) and looser variants: optional hours (MM:SS), optional
# milliseconds, and ',' or '.' as the ms separator.
TIME_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:[,.](\d{1,3}))?")
VSPEAKER_RE = re.compile(r"<v\s+([^>]+)>", re.I)  # WebVTT speaker: <v Sarah>...
TAG_RE = re.compile(r"</?[^>]+>")                  # any remaining markup tags


def parse_ts(token):
    m = TIME_RE.search(token)
    if not m:
        return None
    h, mm, ss, ms = m.groups()
    h = int(h) if h else 0
    ms = int(ms.ljust(3, "0")) / 1000.0 if ms else 0.0
    return h * 3600 + int(mm) * 60 + int(ss) + ms


def clean_text(s):
    """Strip subtitle markup while keeping speaker names readable."""
    s = VSPEAKER_RE.sub(r"\1: ", s)  # <v Sarah>text</v> -> "Sarah: text"
    s = TAG_RE.sub("", s)            # drop </v>, <c>, inline <00:00:00.000>, etc.
    return re.sub(r"\s+", " ", s).strip()


def parse_srt(text):
    """Return a list of cues: [{"start": float, "end": float, "text": str}]."""
    # Normalize newlines and split into blocks on blank lines.
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n").strip())
    cues = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        # Find the line containing the "-->" timing arrow.
        ts_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if ts_idx is None:
            continue
        left, _, right = lines[ts_idx].partition("-->")
        start, end = parse_ts(left), parse_ts(right)
        if start is None:
            continue
        body = clean_text(" ".join(ln.strip() for ln in lines[ts_idx + 1:]))
        if not body:
            continue
        cues.append({"start": start, "end": end if end is not None else start, "text": body})
    cues.sort(key=lambda c: c["start"])
    return cues


def fmt(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def chunk_cues(cues, window_s, overlap_s, min_tail_s):
    if not cues:
        return []
    n = len(cues)
    spans = []  # [i, j) cue-index ranges
    i = 0
    while i < n:
        win_start = cues[i]["start"]
        win_end = win_start + window_s
        j = i
        while j < n and cues[j]["start"] < win_end:
            j += 1
        spans.append([i, j])
        if j >= n:
            break
        # Step back by overlap so the next window re-includes the tail.
        next_start_time = cues[j]["start"] - overlap_s
        k = j
        while k > i and cues[k - 1]["start"] >= next_start_time:
            k -= 1
        i = max(k, i + 1)  # always make progress

    # Absorb a too-short final window into the previous one. Its content is
    # already covered by the overlap, so a tiny trailing chunk adds no value and
    # just fragments the last topic across two passes. Extending the previous
    # span to the end is exact because the windows overlap.
    if len(spans) >= 2:
        last_i, last_j = spans[-1]
        tail_dur = cues[last_j - 1]["start"] - cues[last_i]["start"]
        if tail_dur < min_tail_s:
            spans[-2][1] = last_j
            spans.pop()

    chunks = []
    for (i, j) in spans:
        window = cues[i:j]
        lines = [f"[{fmt(c['start'])}] {c['text']}" for c in window]
        chunks.append({
            "chunk_id": len(chunks),
            "start_s": round(window[0]["start"], 3),
            "end_s": round(window[-1]["start"], 3),
            "text": "\n".join(lines),
        })
    return chunks


def main():
    ap = argparse.ArgumentParser(description="Chunk an SRT into overlapping windows for LLM chaptering.")
    ap.add_argument("srt", help="Path to the .srt file")
    ap.add_argument("--window-seconds", type=float, default=1800.0, help="Window length (default 1800 = 30 min)")
    ap.add_argument("--overlap-seconds", type=float, default=90.0, help="Overlap between windows (default 90)")
    ap.add_argument("--min-tail-seconds", type=float, default=300.0,
                    help="Absorb a final chunk shorter than this into the previous one (default 300 = 5 min)")
    args = ap.parse_args()

    try:
        with open(args.srt, encoding="utf-8-sig") as f:
            raw = f.read()
    except OSError as e:
        print(f"error: cannot read {args.srt}: {e}", file=sys.stderr)
        sys.exit(1)

    cues = parse_srt(raw)
    if not cues:
        # Not a hard gate: this script is a fast path, not the only way in.
        # Emit a structured signal so the skill can fall back to reading the
        # raw transcript directly instead of failing.
        json.dump({
            "ok": False,
            "cue_count": 0,
            "reason": "no timestamped cues found (no blank-line-separated blocks with a '-->' line)",
            "fallback": "read the raw file directly and segment from its inline timestamps",
        }, sys.stdout, ensure_ascii=False, indent=2)
        print()
        sys.exit(2)

    chunks = chunk_cues(cues, args.window_seconds, args.overlap_seconds, args.min_tail_seconds)
    duration = cues[-1]["end"]
    out = {
        "ok": True,
        "total_duration_s": round(duration, 3),
        "total_duration_hms": fmt(duration),
        "cue_count": len(cues),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
