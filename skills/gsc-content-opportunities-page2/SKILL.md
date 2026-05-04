---
name: gsc-content-opportunities-page2
description: >
  Surface quick-win content optimization targets — queries where the
  site ranks on page 2 (positions 11–20) with high impressions but low
  CTR. Emits title / meta-description recommendations per opportunity.
  Distinct from the existing find_gsc_content_opportunities tool which
  surfaces "near page 1" positions 4–10. Activate when the user says
  "content opportunities page 2", "low CTR fixes", "page 2 SEO wins",
  or "ranking but not clicked".
---

# GSC Content Opportunities (Page 2) — Spain

Targets a specific, high-leverage pattern: queries where the site is
**ranking but not being clicked on**. These are pages stuck on page 2
or just below the fold with meaningful search volume. The fix is
usually title + meta improvements, internal-linking boosts, or content
depth — not new content.

Complements the existing `find_gsc_content_opportunities` tool
(positions 4–10, "almost page 1, push for top 3"). This skill targets
the next tier: positions 11–20, "ranking but hidden".

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 28 days
- Fail fast on missing input.

## Client Brief

Read `clients/briefs/<client_id>.md`. Different verticals tolerate
different CTR baselines — LeadGenCo's financial queries have lower CTR
than WellnessBrand's wellness queries. Use the brief to set an informed
expected CTR.

## Data Collection (MCP Tools)

1. `get_gsc_advanced_analytics` with:
   - `dimensions: ["query", "page"]`
   - `sort_by: "impressions"`
   - `sort_direction: "descending"`
   - `row_limit: 1000`
   - period from inputs

## Filter + Scoring

Client-side filter to rows where ALL of:
- `position` ≥ 11 AND `position` ≤ 20
- `impressions` > 100
- `ctr` < 0.03 (3% — below average for these positions)

Compute **Opportunity Score** per row:

```
opportunity_score = impressions × (0.05 − ctr)
```

This approximates clicks gained if CTR reaches 5% (a realistic target
for positions 11–20 with better snippets).

Sort by opportunity_score descending. Keep top 20.

## Recommendations per Opportunity

For each top-20 entry, emit:

1. **Title test idea** — shorter + query at the front, or a
   number/year hook, or a benefit-led rewrite
2. **Meta description test idea** — include the primary query,
   state the benefit, end with a CTA
3. **Internal linking** — identify 2–3 existing high-authority pages
   that could link to this URL with the query as anchor text
4. **Content depth check** — flag if the query is head-term wide but
   the page is narrow (or vice versa)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-gsc-content-opps-p2/`:

- `GSC-CONTENT-OPPS-PAGE2-REPORT.md` — primary report
- `GSC-OPPORTUNITIES-TABLE.md` — sortable table (query, page,
  position, impressions, CTR, opportunity_score)

First non-empty line of `GSC-CONTENT-OPPS-PAGE2-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: gsc PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — total opportunity score, top 5 quick wins
2. **Top 20 Opportunities** — one block per row with table + specific
   title / meta / internal-linking recommendations
3. **Patterns** — if ≥ 5 opportunities share a page or a template,
   flag as a systemic CTR issue (one template fix covers many queries)

## Hard Rules

- **CTR target of 5%** is a baseline — the brief may justify a
  different target (e.g. 2% is more realistic for very-head terms
  like "insurance")
- **Never recommend keyword stuffing** in titles — if the query
  requires stuffing to fit, it's the wrong query for that page
- **Low-value queries** (impressions < 100 or informational-only
  terms with no commercial intent) are filtered out — don't re-add
  them in the report
- This skill's output NEVER contradicts `find_gsc_content_opportunities`
  (positions 4–10) — they cover different position bands and can run
  in parallel
