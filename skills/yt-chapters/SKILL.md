---
name: yt-chapters
description: Generate semantic YouTube chapters with timestamps from an SRT subtitle file. Boundaries are placed on meaning shifts (a new question, a topic change, a demo starting), not fixed time intervals. Handles very long transcripts by chunking and reassembling. Use when a user has an .srt (or transcript with timestamps) and wants a YouTube chapter list for the video description.
---

# YouTube Semantic Chapters

Turn an SRT subtitle file into a clean, YouTube-valid chapter list whose
boundaries reflect how the *content* actually shifts.

## Output language

Detect the language of the SRT and write chapter titles in that language by
default. If the user requested a specific output language, use that instead.

## Workflow

### 1) Chunk the SRT

Always chunk first (one command works for any length):

```bash
python scripts/srt_chunk.py <file.srt>
```

Defaults: **30-minute windows with 90-second overlap**. This is sized so most
videos (≤30 min) come back as a **single chunk** — best segmentation quality, no
reassembly needed. Only long content (podcasts, streams, lectures) splits into
multiple chunks. 30 min ≈ 8–9k tokens, so even a 90-minute multi-chunk video fits
context comfortably; the window is about segmentation quality, not context limits.

- Tune with `--window-seconds` / `--overlap-seconds` only when needed: raise
  overlap (e.g. `--overlap-seconds 120`) for fast, transition-heavy talk;
  consider a smaller window (e.g. 1200) only if a single huge chunk produces
  coarse, "lost-in-the-middle" boundaries.

This prints JSON: `total_duration_hms`, `cue_count`, and `chunks[]`, where each
chunk's `text` is timestamped lines like `[MM:SS] spoken text`. The overlap means
a boundary near a chunk edge is visible in both neighbouring chunks. The parser
tolerates non-standard SRT: WebVTT `<v Speaker>` tags (normalized to `Speaker:`),
missing index numbers, `MM:SS` / no-millisecond timestamps, and speaker prefixes
like `John:` are kept — a **speaker change is itself a chapter signal**.

**The script is a fast path, not a hard gate.** Its only structural assumptions
are blank-line-separated blocks each containing a `-->` line. If the file doesn't
match (output `"ok": false`, exit 2) — or if `cue_count` looks far too low for the
content — **don't fail: read the raw transcript file directly and segment from its
inline timestamps yourself.** Treat whatever timestamps the file carries (any
recognizable `HH:MM:SS` / `MM:SS` markers) as the boundary times. The deterministic
validator in step 3 still runs regardless of which path produced the boundaries.

### 2) Propose boundaries per chunk (your judgement)

Read each chunk and decide where a viewer would want to jump. Read
`references/chaptering.md` for the boundary signals (new question posed, topic
shift, "let's move on", demo/example start, enumerated points, Q&A turn). Aim for
one chapter every roughly 1–4 minutes; let the content dictate, not the clock.

For each boundary, record the **absolute** `[MM:SS]` from the chunk line and a
concise title (20–50 chars). Collect proposals across all chunks into one JSON
array: `[{"time": "MM:SS", "title": "..."}, ...]`.

### 3) Reassemble + validate

Across overlapping chunks you'll get near-duplicate boundaries — keep one. Then
run the deterministic gate (it sorts, dedupes, snaps the first chapter to 00:00,
enforces the ≥10s gap, and requires ≥3 chapters):

```bash
echo '<your JSON array>' | python scripts/validate_chapters.py --duration-seconds <total_s>
```

- Exit 0 → use the returned `youtube_block` and `chapters`. Surface any `warnings`.
- Exit 3 → read `errors` and re-segment with finer boundaries, then re-validate.
  This validate→fix→revalidate loop is mandatory; never emit unvalidated chapters.

### 4) Return

Emit a `## CHAPTERS` block with the `youtube_block` (ready to paste into a
description). The first line is always `00:00`.

## Notes

- The `[MM:SS]` markers in chunk text are start times — use them verbatim as boundaries.
- Past 60 minutes, timestamps become `H:MM:SS`; the scripts handle this.
- Chapters require a video ≥10 min to display on YouTube; still produce them for shorter videos if asked (they remain useful description anchors).
