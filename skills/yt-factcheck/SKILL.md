---
name: yt-factcheck
description: Fact-check a video script or transcript, flag likely errors with suggested corrections, and gather reference links to original sources from trustworthy domains only. Uses the built-in WebSearch tool. Use when a user wants their content verified before publishing or wants authoritative source links for the description.
---

# Fact-Check & Trusted References

Verify the factual claims in a script, propose corrections for likely errors, and
collect citations to original sources — restricted to trustworthy domains.

This skill produces TWO outputs from one web-research pass: a **fact-check report**
(verdicts + corrections) and a **references list** (the trustworthy links found),
which `yt-description` can reuse.

## Output language

Write verdicts, corrections, and explanations in the language of the input
content by default; honor an explicit target-language request. Keep source titles
and URLs as-is.

## Workflow (see references/factcheck-pipeline.md for detail)

### 1) Extract atomic, check-worthy claims
Pull out **verifiable factual statements** — numbers, dates, names, attributions,
causal/historical/scientific claims. Skip opinions, jokes, and predictions.
**Decontextualize** each claim: resolve pronouns and references so it stands alone
("he discovered it in 1905" → "Einstein published special relativity in 1905").

### 2) Verify each claim with WebSearch
For each claim, use the built-in **WebSearch** tool. Prefer queries that surface
primary/authoritative sources. Consult `references/trusted-domains.md` and only
rely on results from those categories (gov/intergovernmental, academic/peer-
reviewed, major reference works, established news wires, recognized fact-checkers).
If you must use WebFetch to read a page, do so only for trusted domains.

### 3) Judge
For each claim assign: **Supported / Refuted / Misleading / Unverifiable**, with:
- a one-line explanation,
- the suggested **correction** (for Refuted/Misleading),
- the supporting source URL(s) from trusted domains.

Default to **Unverifiable** rather than guessing when trusted sources don't
clearly confirm. Never fabricate a source or URL — only cite pages you actually
retrieved via WebSearch/WebFetch.

### 4) Assemble references
Collect the distinct trusted URLs used into a clean references list (source name —
domain — url), deduped. This is the links list for the description.

## Return

Two blocks:

```
## FACTCHECK
| Claim | Verdict | Correction | Source |
|---|---|---|---|
| ... | Refuted | ... | <url> |

## REFERENCES
- <Source name — domain>: <url>
```

If no claims need checking, say so explicitly rather than padding the report.
