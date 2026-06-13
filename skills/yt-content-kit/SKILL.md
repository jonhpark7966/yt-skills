---
name: yt-content-kit
description: Orchestrator for YouTube content creation from a script and/or SRT subtitle file. Routes to the right sub-skill (title, description, chapters, fact-check) or runs the full pipeline to produce a complete publishing package — recommended title, description with chapters, fact-check with corrections, and trustworthy source links. Use when a YouTube creator provides a script/transcript/SRT and wants metadata, verification, or the whole package.
---

# YouTube Content Kit (router)

Entry point for the YouTube creator skill suite. Figures out what the user wants,
detects the content language once, and delegates to the specialized sub-skills.

## Sub-skills

| Skill | Produces | Needs |
|---|---|---|
| `yt-chapters` | timestamped semantic chapters | SRT (timing) |
| `yt-title` | title candidates + pick | script or SRT text |
| `yt-description` | full description (embeds chapters + references) | script + chapters (+ references) |
| `yt-factcheck` | verdicts, corrections, trusted source links | script or SRT text; built-in WebSearch |

## Step 1 — Gather inputs & detect language

- Collect what the user has: a **script** (written content), an **SRT** file, or both.
  If neither is present, ask for at least one. The SRT is required for chapters;
  the script (or SRT text) feeds title/description/fact-check.
- **Detect the input language** from the script/SRT once. Output everything in that
  language by default. If the user named a target language, use that for all
  sub-skills and pass it through explicitly.

## Step 2 — Route by intent

- **"Title"** → `yt-title`.
- **"Chapters" / "timestamps"** → `yt-chapters`.
- **"Description"** → `yt-description` (it will pull chapters via `yt-chapters`,
  and references via `yt-factcheck` if the user wants sources).
- **"Fact-check" / "verify" / "sources" / "references"** → `yt-factcheck`.
- **"Everything" / "full package" / unspecified but broad** → run the full pipeline.

When invoking a sub-skill, pass the shared context: `script_text`, `srt_path`, and
`language`. Each sub-skill returns a labeled block (`## TITLE`, `## CHAPTERS`,
`## DESCRIPTION`, `## FACTCHECK`, `## REFERENCES`).

## Step 3 — Full pipeline order

Respect dependencies:

1. `yt-chapters` (SRT → chapters block).
2. `yt-factcheck` (script → verdicts + corrections + trusted references).
3. `yt-title` (script → recommended title).
4. `yt-description` (script + chapters block + references → full description).
5. **Assemble** the final package and present all blocks together:
   - `## TITLE` (recommended + alternatives)
   - `## DESCRIPTION` (with chapters and references embedded, ready to paste)
   - `## FACTCHECK` (table of claims, verdicts, corrections)
   - `## REFERENCES` (trusted source links)

## Step 4 — Final checks

- Title ≤100 chars; description ≤5,000 chars; chapters start at `00:00` with ≥3 entries.
- Everything in the correct output language.
- Corrections are actionable; sources are from trusted domains only and not fabricated.
- Surface any warnings from the validators and any `Unverifiable` claims so the
  creator can decide before publishing.

## Notes

- Fact-check and references come from a single web-research pass in `yt-factcheck`;
  don't duplicate searches in the description step.
- This suite is designed to grow — new creator skills (thumbnail prompts, tags/SEO,
  clip finder, etc.) plug in by following the same `{script_text, srt_path,
  language}` input contract and returning a labeled block.
