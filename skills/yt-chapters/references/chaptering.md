# Semantic chaptering guide

Place chapter boundaries where the *content* turns, so a viewer can jump to the
part they want. Ignore fixed time intervals — a 90-second segment and a 6-minute
segment can both be one chapter if each holds a single coherent idea.

## Boundary signals (place a chapter at these)

- **A new question is posed** — "So what is X?", "But why does this happen?"
  Rhetorical or audience questions usually open a new section.
- **Explicit transitions** — "let's move on", "next", "now that we've covered…",
  "the second thing", "finally", "to wrap up".
- **Topic shift** — the subject noun changes (from *causes* to *solutions*, from
  *theory* to *demo*).
- **Format change** — intro → main content, explanation → live demo/example,
  content → sponsor/ad read, main → Q&A, → conclusion/outro.
- **Enumerated structure** — "step 1 / step 2", "reason one / reason two",
  "first / second / third" each become a chapter.
- **Speaker or scene change** in interviews/panels.

## Title style

- 20–50 characters (hard cap 100; longer truncates on mobile).
- Descriptive and specific, not clickbait: "How black holes form" not "MIND-BLOWING!".
- Match the input language.
- Parallel phrasing across chapters reads well (all noun phrases, or all questions).
- The first chapter (00:00) is usually "Intro", "Introduction", or a hook label.

## Density

- Rough target: a chapter every 1–4 minutes, but driven by content, not the clock.
- Minimum 3 chapters (YouTube requirement). If the content genuinely has fewer
  natural breaks, split the longest sections at their strongest internal shift.
- Avoid micro-chapters: every chapter must be ≥10 seconds (the validator enforces
  this and drops violators).

## Handling overlap between chunks

`srt_chunk.py` overlaps windows so an idea straddling a cut is visible in both
chunks. When you propose boundaries per chunk you may produce two boundaries a
few seconds apart for the same shift — keep the one at the true start of the new
topic; the validator also drops any boundary <10s after the previous one.
