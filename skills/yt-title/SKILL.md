---
name: yt-title
description: Recommend YouTube video titles from a content script or transcript. Produces several candidates optimized for clarity, search, and click-through, then recommends one. Use when a user wants title ideas for a video and has the script, transcript, or SRT.
---

# YouTube Title Recommender

Generate strong title options from the video's content and recommend the best.

## Output language

Write titles in the language of the input script/SRT by default; honor an
explicit target-language request from the user.

## Inputs

Work from whatever is available: a written script, a transcript, or an SRT (use
its spoken text). Identify the core topic, the payoff/hook, and the primary
keyword a viewer would search.

## Rules (see references/seo-title.md for detail)

- **Hard cap 100 characters.** Aim for **65–80** so it doesn't truncate.
- **Front-load the primary keyword** in the first ~40 characters — YouTube weights
  early words and that's what shows before truncation.
- Be specific and honest; no clickbait the content can't pay off.
- One idea per title. Numbers, concrete outcomes, and curiosity gaps help CTR.
- Avoid ALL CAPS spam and keyword stuffing.

## Workflow

1. Extract topic, payoff, and primary keyword from the content.
2. Generate **5 candidates spread across a sensational → refined spectrum** so the
   creator can pick where on the risk curve they want to sit:

   | # | Type | Character |
   |---|---|---|
   | 1 | **Bold / high-arousal** | Most clickable, highest CTR potential — but risks reading as clickbait or low-brow to some viewers. Strong emotion, curiosity gap, or surprise. Still must be honest. |
   | 2 | **Punchy / mainstream** | Energetic and broadly appealing without feeling cheap. The "safe high-performer." |
   | 3 | **Clear / benefit-led** | States the value plainly. Trustworthy, neutral tone. |
   | 4 | **Refined / understated** | Tasteful and credible, not sensational. Suits expert/educational/premium audiences. |
   | 5 | **SEO / keyword-led** | Optimized for search discovery; exact-phrase front-loaded. |

3. For each candidate note: the **type**, the **character count**, and a one-line
   **trade-off** (who it wins, what it risks).
4. Recommend one as the default and say why — but make clear the choice is the
   creator's call on tone/brand. If the content is sensitive (health, finance,
   news), lean the recommendation toward the refined/clear end and flag the bold
   option's risk explicitly.

All five must be **honest to the content** — sensational ≠ false. A bold title
the video can't pay off hurts watch time and ranking; never cross into clickbait.

## Return

A `## TITLE` block: the recommended title first (type + char count + why), then the
full set of 5 as a labeled list with each type, char count, and trade-off note.
