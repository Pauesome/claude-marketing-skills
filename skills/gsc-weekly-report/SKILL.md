---
name: gsc-weekly-report
description: >
  Generate a 28-day SEO performance snapshot with period-over-period
  comparison. Surfaces query-level gainers and losers, flags >20%
  click drops, and lists top 10 queries. Cron-friendly — runs weekly
  per client. Activate when the user says "weekly SEO report", "SEO
  snapshot", "MoM SEO", "how is my organic trending", or asks for a
  regular SEO status update.
---

# GSC Weekly Report — Spain

Periodic SEO status report comparing the last 28 days vs the prior
28-day period. Designed to run weekly on a cron schedule — produces
consistent, parseable output that the user can diff over time.

## Required Inputs

- `client_id` (required)
- No date parameters — the skill always uses last-28d vs prior-28d
  (anchored on today minus GSC's 3-day lag). Keeps reports
  comparable across runs.

## Client Brief

Read `clients/briefs/<client_id>.md`. Helps interpret drops — some
are sector-seasonal (LeadGenCo's lead-product queries dip in summer),
some are algorithmic, some are self-inflicted (recent site changes).

## Data Collection (MCP Tools)

1. `get_gsc_queries` — top 10 queries for the current 28d window
2. `get_gsc_pages` — top 10 pages for the current 28d window
3. `compare_gsc_periods` with `dimensions: ["query"]`, `limit: 20`,
   period1 = prior 28d, period2 = current 28d

## Analysis

- Totals: clicks, impressions, CTR (weighted), avg position
  (impressions-weighted). Compare current vs prior.
- Movers: top 10 query gainers (click_diff > 0, sorted desc) + top
  10 query losers (click_diff < 0, sorted asc by value = most
  negative first).
- Alerts: any query where `click_pct <= -20` AND `p1_clicks >= 20`
  (significance filter — ignore micro-queries).
- Top queries: snapshot of current top 10 by clicks.

## Scoring

- **PASS**: overall clicks up or flat, no alert-level drops
- **WARNING**: overall clicks down 5–20%, or up to 3 alert queries
- **FAIL**: overall clicks down > 20%, or > 3 alert queries, or
  total alerts represent > 10% of site clicks

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-gsc-weekly/`:

- `GSC-WEEKLY-REPORT.md` — primary report

First non-empty line of `GSC-WEEKLY-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: gsc PERIOD: <current_start>..<current_end>
```

### Report Structure

1. **Snapshot** — totals table: clicks, impressions, CTR, avg
   position, each with absolute + % delta vs prior period
2. **Alerts** — list of queries with click_pct ≤ -20% (p1_clicks ≥
   20), each with:
   - Query
   - Previous vs current clicks
   - Position change
   - One-sentence hypothesis (from the brief when possible)
   - Recommended next step
3. **Top 10 Gainers** — table: query, click_diff, position_diff
4. **Top 10 Losers** — table: same columns
5. **Top 10 Queries Right Now** — current-period snapshot
6. **Top 10 Pages Right Now** — current-period snapshot

## Hard Rules

- **Never trigger an alert on queries with p1_clicks < 20** — too
  noisy
- **Avg position is impressions-weighted**, not a simple mean —
  otherwise long-tail queries at position 50 drown out head terms
  at position 3
- **Same-period comparison only**: always 28d vs prior 28d. Don't
  mix week-over-week with month-over-month in the same report — use
  a different skill if the user needs weekly cadence
- **Never recommend drastic action on a single week's drop** — flag
  and monitor; recommend immediate action only after 2+ consecutive
  weeks of decline
