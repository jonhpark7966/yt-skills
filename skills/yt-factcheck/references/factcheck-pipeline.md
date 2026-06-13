# Fact-checking pipeline detail

Adapted from established LLM fact-checking pipelines (decompose → checkworthiness
→ query → retrieve → verify) and Claimify-style claim decontextualization.

## 1. Claim extraction
Read the script and list **atomic** factual statements — each asserting one
checkable thing. Split compound sentences ("X happened in 1990 and caused Y") into
separate claims.

Keep (check-worthy):
- statistics, quantities, dates, durations, rankings
- named entities and attributions ("X said/invented/discovered Y")
- historical, scientific, geographic, legal, medical claims
- cause-and-effect assertions stated as fact

Drop (not check-worthy):
- opinions, value judgements, predictions about the future
- jokes, hypotheticals, rhetorical questions
- self-reference ("in this video I'll show…")

## 2. Decontextualization
Rewrite each claim so it is self-contained:
- resolve pronouns (he/she/it/they/this) to the entity named earlier,
- inline the referent of "the company", "that study", "back then",
- carry over the time/place context.
A claim must be verifiable without reading the rest of the script.

## 3. Query generation
For each claim write 1–2 search queries aimed at primary sources. Prefer the
canonical name, the year, and a distinctive keyword. Add `site:` to a trusted
domain when you specifically want the authoritative source (e.g. a `.gov`
statistic, a journal).

## 4. Retrieval (WebSearch)
Run the queries with the built-in WebSearch tool. Scan results; keep only hits on
trusted domains (see `trusted-domains.md`). For a definitive primary source, use
WebFetch to read the page and confirm the exact figure/quote — but only on trusted
domains.

## 5. Verification verdicts
- **Supported** — trusted source(s) confirm the claim as stated.
- **Refuted** — trusted source(s) contradict it. Provide the corrected statement.
- **Misleading** — technically related but missing context / wrong framing /
  outdated. Provide the accurate framing.
- **Unverifiable** — no clear confirmation from trusted sources. Say what's missing.

Rules:
- When trusted evidence is weak or conflicting, choose **Unverifiable** — do not
  guess and do not let the script's own confidence sway the verdict.
- Cite only pages actually retrieved. Never invent a URL or a publisher.
- Prefer the **original/primary** source over an aggregator that merely reports it.
- Note the date for time-sensitive facts (figures change year to year).

## 6. Output
- Fact-check table: Claim | Verdict | Correction | Source.
- References list: deduped trusted URLs, "Source name — domain — url".
- If everything checks out, state "No factual errors found" and still provide the
  reference links gathered.
