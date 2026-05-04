---
name: google-ads-dayparting-analysis
description: >
  Analyse Google Ads performance by hour-of-day and day-of-week to identify
  when campaigns perform best and worst. Produces ad-schedule recommendations
  with statistical-significance filtering (no conclusions from low-volume
  buckets), bid-adjustment proposals, and an estimated savings figure from
  reallocating spend out of underperforming windows. Activate when the user
  says "dayparting", "ad schedule", "day of week performance", "hour of day",
  "what times are best", or asks about when ads should run.
---

# Google Ads Dayparting Analysis — Spain

Uses `get_google_ads_hourly_performance` to break performance down by
day-of-week × hour-of-day, filters noise via statistical-significance
thresholds, and outputs actionable ad-schedule adjustments.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 90 days (need
  volume for per-hour statistical confidence)
- `primary_metric` (optional) — one of `cpa`, `cpc`, `roas`, `ctr`,
  `conversion_rate`. Defaults to `cpa` for lead-gen clients, `roas`
  for e-commerce, inferred from brief.
- `campaign_ids` (optional) — scope to specific campaigns

Fail fast on missing `client_id`.

## Client Brief

Read `clients/briefs/<client_id>.md`:

- **Business hours**: B2B clients (SaaSCo) should expect weekday
  9–18h outperformance; B2C (Ferrer-Ponseti, WellnessBrand) expect
  evening/weekend peaks. Brief sets the expectation baseline.
- **Sales coverage**: if the client's sales team only responds to
  calls 9–18h and call extensions are the primary conversion, ads
  outside business hours convert worse simply because nobody picks
  up. Flag this in the report.
- **Target CPA / ROAS**: calibrates "underperforming" — below target
  = savings opportunity.

If brief is missing, use CPA as default primary metric and run without
business-hours context.

## Data Collection (MCP Tools)

1. `get_google_ads_hourly_performance` — primary data source; returns
   per-campaign × day-of-week × hour-of-day rows
2. `get_google_ads_campaign_performance` — for the same range; used
   to compute account-level averages as comparison baseline

## Statistical Significance Filter

Before drawing conclusions, filter buckets:

- **Minimum bucket volume**: a (day, hour) bucket must have
  ≥ 100 impressions AND ≥ 1 click across the full date range. Below
  that, metrics are unreliable and should be reported as "insufficient
  data", not "underperforming".
- **Minimum conversion volume for CPA/ROAS claims**: a bucket needs
  ≥ 3 conversions before we claim "CPA is €X here". Fewer conversions
  → report directional only, no specific €X recommendation.
- **Significance vs account average**: bucket metric must be > ±20%
  off account average to be flagged. ±20% within 90 days of data
  is typically noise.

Label buckets accordingly:

| Label | Criterion |
|---|---|
| **High performer** | Metric ≥ 20% better than account average AND volume threshold met |
| **Underperformer** | Metric ≥ 20% worse than account average AND volume threshold met |
| **Neutral** | Within ±20% of account average |
| **Insufficient data** | Below volume threshold |

## Recommendation Logic

### Ad schedule (not bid adjustments)
If a block of consecutive hours on a day-of-week is consistently
underperforming AND the cumulative spend in that block is ≥ €20 in
the period:
- Recommend **excluding the block** from the ad schedule
- Compute spend saved, conversions lost, and net effect after
  reallocating the saved spend to top-performing windows at their
  observed CPA

### Bid adjustments (when exclusion is too aggressive)
For Smart Bidding campaigns (tCPA / tROAS / MaxConv), Google already
optimises across hours — explicit bid adjustments are NOT recommended
on Smart Bidding. Report that Smart Bidding handles this automatically.

For Manual CPC / Manual CPM campaigns, recommend hour-of-day bid
adjustments:
- `−50%` for consistent underperformers
- `+20%` for consistent overperformers (with note: Smart Bidding would
  be better than manual bid-ups)

### Business-hours caveat
If brief specifies sales team hours, always include the note: "ads
outside sales hours may convert via form-submission only; evaluate
per-conversion-action performance before excluding".

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-google-dayparting/`:

- `DAYPARTING-REPORT.md` — primary report (with SCORE header)
- `DAYPARTING-HEATMAP.md` — 7×24 grid of the primary metric, one
  per campaign + one account-level
- `DAYPARTING-RECOMMENDATIONS.md` — specific ad-schedule / bid-
  adjustment changes, copy-paste-ready for Google Ads Editor

First non-empty line of `DAYPARTING-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: google_ads PERIOD: <start>..<end> METRIC: <primary_metric>
```

Score = 100 − (underperforming_spend / total_spend × 150), capped
[0, 100]. 10% spend in underperforming windows = 85/100 (B).

### Report Structure

1. **Heatmap Summary** — 7×24 grid, primary metric, colour-coded
2. **High / Low Performer Blocks** — contiguous day-hour blocks
   labelled as above
3. **Recommended Schedule Changes** — per campaign, specific
   day+hour exclusions with spend/conversions impact
4. **Reallocation Opportunity** — spend saved × expected CPA in
   peak windows = projected additional conversions
5. **Smart Bidding Note** — if all campaigns are on Smart Bidding,
   clearly explain that exclusions (not bid adjustments) are the
   right lever
6. **Insufficient-Data Blocks** — listed separately; do not
   recommend action on these

## Hard Rules

- **Never recommend an exclusion on a bucket with < 100 impressions
  or < 3 conversions.** The headline feature of this skill is
  rigour — shipping recommendations on sparse data makes it worse
  than useless.
- **Smart Bidding campaigns: exclusions only, no bid adjustments.**
  Google's auction-time bidding already factors hour/day — manual
  overrides fight the model.
- **For clients with sales-team hours in the brief**, always check
  whether the "underperformance" is just call-conversion unavailability.
- **Never remove >40% of total account hours** — thin schedules
  starve Smart Bidding of signal and can collapse volume.
- **When a campaign has been active < 14 days**, skip it — no stable
  hour × day pattern yet.
