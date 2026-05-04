---
name: gsc-indexing-audit
description: >
  Audit indexing status across a site's top-impression pages using the
  GSC URL Inspection API. Categorizes each page as Indexed,
  Not-Indexed, Canonical-mismatch, Robots-blocked, or Fetch-issue and
  produces a prioritized action list. Activate when the user says
  "indexing audit", "are my pages indexed", "index coverage", or asks
  why paid-campaign landing pages aren't appearing in Google.
---

# GSC Indexing Audit — Spain

Diagnostic audit that answers: **are my most valuable pages actually
indexed?** Search-analytics tools can show a page is receiving
impressions, but only URL Inspection reveals indexing status, canonical
decisions, and crawl/robots state. A paid landing page that Google has
decided not to index is invisible — you're paying for clicks that may
not sustain organic halo.

## Required Inputs

- `client_id` (required) — client must have `gsc` configured
- `date_range_start` / `date_range_end` — default last 28 days (GSC has
  ~3-day lag). Used only to pick the top-impression page list.
- Fail fast on missing input; no mid-audit prompts.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to
interpret findings: a LeadGenCo landing page with `Not-Indexed` is an
emergency (each missed indexation = lost lead-product lead); a
ContentCo blog post with `Not-Indexed` is lower priority (it's a
content-marketing asset, not a revenue page). Sector determines
severity weighting.

## Data Collection (MCP Tools)

1. `get_gsc_pages` — top 20 pages by clicks for the period, pulled
   from `client.gsc.site_url`
2. For each batch of ≤ 10 pages: `inspect_gsc_urls({ urls: […10 pages] })`
   Call twice if 11–20 pages need inspection. Parallel execution within
   each batch is handled by the service.

## Categorization Logic

For each inspected URL, bucket into ONE category (first match wins):

| Category | Rule |
|---|---|
| **Indexed** | `verdict === "PASS"` AND `coverage_state` contains "indexed" |
| **Canonical-mismatch** | `google_canonical` != `user_canonical` AND both present |
| **Robots-blocked** | `robots_txt_state === "BLOCKED"` |
| **Fetch-issue** | `page_fetch_state !== "SUCCESSFUL"` |
| **Not-Indexed** | everything else (verdict != PASS, or coverage says "not indexed"/"excluded") |

## Severity Scoring

- **Critical** (severity ×5): Not-Indexed on a page with > 100 clicks
  (previous 28 days) or on a page listed as a paid-campaign landing
  page in the brief
- **High** (×3): Canonical-mismatch on a page with > 50 clicks
- **Medium** (×2): Robots-blocked or Fetch-issue on any page that has
  impressions
- **Low** (×1): Soft-excluded pages with minimal traffic

## Scoring

Each inspected URL: PASS (Indexed or low-severity Not-Indexed) = 100%,
WARNING (recoverable issue) = 50%, FAIL (Critical Not-Indexed) = 0%.
Apply severity multiplier, normalize, weighted average → overall score.
A Critical failure caps the grade at C.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-gsc-indexing-audit/`:

- `GSC-INDEXING-REPORT.md` — primary report
- `GSC-NOT-INDEXED.md` — full list of not-indexed URLs with
  coverage_state and recommended action
- `GSC-CANONICAL-MISMATCHES.md` — google_canonical vs user_canonical
  per URL

First non-empty line of `GSC-INDEXING-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: gsc PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — count by category, Critical count, score
2. **Category Breakdown** — per-bucket table with URL, coverage state,
   clicks (last 28d), recommended action
3. **Critical Actions** — Not-Indexed pages with paid-landing-page
   context from the brief
4. **Canonical Decisions** — Google chose X instead of Y: list with
   recommended fix (update canonical, merge content, 301 redirect)
5. **Crawl / Robots Issues** — pages Google can't reach
6. **Confidence Note** — if fewer than 20 pages have impressions,
   small-sample warning

## Hard Rules

- **Quota**: URL Inspection is 2,000 calls/property/day. Top-20
  inspection uses 20 calls — safe. Never inspect the same URL twice in
  one skill run.
- **Never recommend noindex** on a page ranking for anything with
  impressions. If a page should be noindex, it shouldn't be in the
  top-20 by impressions in the first place.
- **Canonical mismatches**: always recommend updating the user
  canonical to match Google's choice UNLESS the brief explicitly
  states the page must rank on the user's preferred URL (brand
  protection, campaign landing).
- **Pages with zero clicks and zero impressions**: exclude from the
  audit entirely — nothing to score.
