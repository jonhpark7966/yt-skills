# YouTube description template & rules

## Limits
- **5,000 characters** hard maximum.
- Only the first **~150 characters** show before "Show more" and in search results
  — they must carry the hook and primary keyword. No "Welcome to my channel"
  boilerplate before the hook.
- Plain text only (no markdown rendering). Use emoji/section labels for structure.

## Canonical layout

```
<Hook line 1 — what the viewer gets, keyword front-loaded>
<Hook line 2 — optional, still within first 150 chars>

<Summary: 2–4 sentences. The topic, the angle, who it's for.>

⏱️ Chapters
00:00 Intro
01:35 <...>
<paste the validated chapters block verbatim>

🔗 References & Sources
- <Source name — domain>: <https://...>
- <Source name — domain>: <https://...>

▶️ <Optional: related video / playlist / CTA>

#PrimaryKeyword #SecondaryKeyword #Topic
```

## Section notes
- **Hook**: the single most important text. Front-load the keyword; promise the payoff.
- **Summary**: expand the hook; weave in secondary keywords naturally (no stuffing).
- **Chapters**: must come from `yt-chapters` and start at `00:00`. Do not hand-edit
  timestamps — re-run the chapter skill if they need to change.
- **References**: only vetted, trustworthy links (from `yt-factcheck`). Label each
  with the source and domain so viewers can see credibility at a glance. Omit the
  whole section if there are no sources rather than padding it.
- **Hashtags**: 3–5. The first three appear as clickable links above the video title.

## Length check
Target 1,000–2,000 characters total. If over 5,000, trim the summary and trailing
CTA first — never the chapters or references.
