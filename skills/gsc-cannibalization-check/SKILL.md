---
name: gsc-cannibalization-check
description: >
  Detect keyword cannibalization — queries where two or more pages on
  the same site compete for the same ranking. Produces consolidation
  recommendations (canonical, redirect, or content merge). Activate
  when the user says "keyword cannibalization", "competing pages",
  "keyword overlap", or "which of my pages should rank".
---

# GSC Keyword Cannibalization Check — Spain

Identifies queries where multiple pages on the client's site are
competing for the same rankings. Cannibalization splits authority,
confuses Google's ranking choice, and typically costs clicks across
the affected query set. The fix is usually consolidation — pick the
winner, redirect the rest, or merge the content.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 28 days
- Fail fast on missing input.

## Client Brief

Read `clients/briefs/<client_id>.md`. Large content sites
(ContentCo) generally have more legitimate topic variations than
lead-gen sites (LeadGenCo) where cannibalization usually means
administrative duplication (wrong canonical, legacy page, duplicate
landing page). Use the brief to weight severity.

## Data Collection (MCP Tools)

1. `get_gsc_advanced_analytics` with:
   - `dimensions: ["query", "page"]`
   - `sort_by: "impressions"`
   - `sort_direction: "descending"`
   - `row_limit: 1000`
   - period from inputs

## Cannibalization Logic

Group rows by query. A query is a cannibalization candidate if:

- ≥ 2 distinct pages appear
- Combined impressions ≥ 100 (filter out noise)
- At least one page has position ≤ 20 (ranking meaningfully)

For each candidate query, collect:
- Every page with its individual clicks, impressions, CTR, position
- Total impressions across competing pages (value at stake)
- Winner candidate = page with best position; if tied, best CTR; if
  still tied, most clicks

## Severity

- **High**: ≥ 3 pages competing OR combined impressions > 1000
- **Medium**: 2 pages competing AND impressions 200–1000
- **Low**: 2 pages competing AND impressions 100–200

## Scoring

Each cannibalization case contributes a FAIL (High) / WARNING (Medium)
/ note (Low). Overall score inversely proportional to cannibalization
impressions as share of total site impressions.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-gsc-cannibalization/`:

- `GSC-CANNIBALIZATION-REPORT.md` — primary report
- `GSC-CANNIBALIZATION-MATRIX.md` — full query × page matrix sorted
  by total impressions

First non-empty line of `GSC-CANNIBALIZATION-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: gsc PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — candidate count by severity, total
   impressions at stake, score
2. **Top 20 Cannibalization Cases** — one block per query with:
   - Query
   - Competing pages table (URL, position, CTR, clicks, impressions)
   - Recommended winner + rationale
   - Fix: canonical / 301 redirect / content merge / leave (if
     intent differs enough)
3. **Systemic Patterns** — if > 10 cases share a URL pattern (e.g.,
   `/blog/` vs `/insights/`), flag as architectural issue

## Hard Rules

- **Never recommend merging pages with genuinely different intent**
  (e.g. a blog post and a product page ranking for the same head
  term — the product page usually wins naturally; the blog post
  serves a different funnel stage)
- **Consolidation recommendation order**: (1) update canonical on
  losers → (2) if canonicals don't resolve cannibalization after 6
  weeks, 301-redirect the losers → (3) content-merge only as a last
  resort (high effort, risk of losing long-tail queries)
- When brief indicates the "loser" URL is a paid-campaign landing
  page, DO NOT recommend redirecting it — flag the cannibalization
  but recommend fixing the internal linking / topical authority on
  the non-landing page instead
