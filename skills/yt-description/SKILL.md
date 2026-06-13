---
name: yt-description
description: Write a complete YouTube video description with a hook, summary, timestamped chapters, reference links, and hashtags, assembled from a script/transcript plus a chapters list. Use when a user wants a ready-to-paste description. Pairs with yt-chapters (for the chapter block) and yt-factcheck (for reference links).
---

# YouTube Description Builder

Assemble a publish-ready description. The first ~150 characters are prime real
estate (shown above "Show more" and in search) — lead with the hook there.

## Output language

Match the language of the input content by default; honor an explicit
target-language request.

## Inputs

- Script or transcript (for the hook + summary).
- A **chapters block** — if not provided, invoke `yt-chapters` first to produce it.
- **Reference links** — if the user wants sources, invoke `yt-factcheck` and use
  its trusted-source links. Otherwise omit the references section.

## Structure (see references/description-template.md)

```
[Hook — 1–2 lines, keyword-rich, <150 chars total before the fold]

[2–4 sentence summary of what the video covers and who it's for]

⏱️ Chapters
00:00 ...
<the validated chapters block>

🔗 References
- <Title — domain>: <url>
...

#keyword1 #keyword2 #keyword3
```

## Rules

- **Hard cap 5,000 characters.** Practical target 1,000–2,000.
- First **150 characters** = the hook (no boilerplate before it).
- Chapters: paste the block verbatim from `yt-chapters` — the first line MUST be `00:00`.
- References: only include links vetted as trustworthy (from `yt-factcheck`). Label
  each with its source/domain. Never invent URLs.
- Hashtags: 3–5 relevant tags at the end (the first 3 also surface above the title).
- Plain text only — YouTube descriptions don't render markdown.

## Workflow

1. Gather script, chapters block, and (optional) references.
2. Write the hook (front-load the main keyword), then the summary.
3. Insert the chapters block, then references, then hashtags.
4. Check total length ≤5,000 chars and that line 1 of chapters is `00:00`.
5. Return a `## DESCRIPTION` block, ready to paste.
