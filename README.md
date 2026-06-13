# yt-skills

A suite of [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
for YouTube content creators. Give it a script and/or an `.srt` subtitle file and
it produces a publish-ready package: a recommended **title**, a **description with
chapters**, a **fact-check with corrections**, and **trustworthy source links**.

## Skills

| Skill | Role |
|---|---|
| **yt-content-kit** | Router/orchestrator — detects intent, runs single tasks or the full pipeline |
| **yt-chapters** | SRT → semantic chapters (LLM-decided boundaries; chunks long files and reassembles) |
| **yt-title** | Title candidates + recommendation (SEO + CTR aware) |
| **yt-description** | Full description: hook, summary, chapters, references, hashtags |
| **yt-factcheck** | Claim verification + corrections + trusted-source links (built-in WebSearch) |

## How it fits together

```
                 ┌─────────────────┐
 script + .srt → │  yt-content-kit  │  (router: detect intent + language)
                 └────────┬────────┘
        ┌─────────────┬───┴────┬──────────────┐
        ▼             ▼        ▼              ▼
   yt-chapters   yt-factcheck  yt-title   yt-description
   (chapters)    (corrections  (title)    (assembles all
                  + references)             into final desc)
```

Full-pipeline order: chapters → fact-check → title → description → assemble.

## Design principles

- **Output language follows the input** by default; an explicit user request overrides.
- **Deterministic where it must be**: SRT chunking and YouTube chapter-rule
  enforcement are Python scripts (`yt-chapters/scripts/`, stdlib-only); judgement
  tasks (segmentation, titles, verification) are LLM-driven.
- **Trustworthy sources only**: fact-check restricts to an authoritative
  domain allowlist (`yt-factcheck/references/trusted-domains.md`) and never
  fabricates URLs.
- **Extensible**: new creator skills plug in via the shared
  `{script_text, srt_path, language}` input contract and a labeled output block.

## YouTube rules enforced

- Chapters: first at `00:00`, ≥3 chapters, ascending, ≥10s each, titles ≤100 chars.
- Title: ≤100 chars (65–80 ideal, keyword front-loaded).
- Description: ≤5,000 chars, hook in the first ~150.

## Requirements

- **Python 3.8+** — the only two scripts (`srt_chunk.py`, `validate_chapters.py`)
  use the standard library only; nothing to install.
- A host with web access (e.g. **Claude Code**) for the fact-check / references
  stage, which uses the built-in `WebSearch` tool. The other stages work offline.

## Usage

Drop the `skills/` directory where your agent loads skills (for Claude Code, e.g.
`~/.claude/skills/` or a plugin), then ask in natural language — the router skill
(`yt-content-kit`) picks the right sub-skill:

- "Give me chapters for this SRT" → `yt-chapters`
- "Suggest titles for this video" → `yt-title`
- "Write the full description" → `yt-description`
- "Fact-check this script and find sources" → `yt-factcheck`
- "Do everything for this video" → full pipeline

## Scripts

```bash
# Chunk a long SRT into overlapping windows for chaptering
# (defaults: 30min window / 90s overlap; a <5min trailing chunk is absorbed)
python skills/yt-chapters/scripts/srt_chunk.py transcript.srt

# Validate/repair proposed chapters against YouTube rules
echo '[{"time":"00:00","title":"Intro"}, ...]' | python skills/yt-chapters/scripts/validate_chapters.py
```

## Roadmap

Planned additions to the suite: thumbnail-prompt generator, tags/SEO keyword
skill, clip/short finder, end-screen & pinned-comment drafting, multi-language
localization pass.

## License

[MIT](LICENSE) © 2026 Jong Hyun Park
