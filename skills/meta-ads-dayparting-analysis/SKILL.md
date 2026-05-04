---
name: meta-ads-dayparting-analysis
description: >
  Analyse Meta Ads (Facebook + Instagram) performance by hour-of-day and
  day-of-week in the audience time zone. Produces ad-set scheduling
  recommendations with statistical-significance filtering. Meta-specific
  nuance: Advantage+ campaigns and Advantage budget don't support custom
  schedules, so this skill guides when exclusion is feasible vs when bid
  adjustments on ad sets are the right lever. Activate when the user says
  "meta dayparting", "facebook ad schedule", "instagram hour of day",
  "when does meta perform best", or asks about Meta ad timing.
---

# Meta Ads Dayparting Analysis — Spain

Uses `get_meta_hourly_performance` to segment Meta campaign performance
by hour and day-of-week, applies significance filtering, and outputs
ad-set scheduling recommendations.

Different from Google dayparting because:
- Meta only supports **ad-set-level custom schedules**, and only with
  **Lifetime Budgets** (daily-budget ad sets can't have custom schedules)
- Advantage+ Shopping / Sales campaigns auto-optimise timing — manual
  scheduling is not available
- Meta's hourly breakdown returns data in **the audience's time zone**,
  not the advertiser's — which matters for multi-geo campaigns

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 90 days
- `primary_metric` (optional) — one of `cpa`, `cpc`, `roas`, `ctr`,
  `conversion_rate`. Default `cpa` for lead-gen, `roas` for e-commerce
  (infer from brief)
- `campaign_ids` (optional) — scope to specific campaigns

## Client Brief

Read `clients/briefs/<client_id>.md`:

- **Audience time zone**: Meta's hourly breakdown is in the audience's
  local time. For Spain-targeted campaigns it aligns with CET/CEST;
  for cross-border (e.g. Latin America targeting) the hours may look
  displaced.
- **Business type**: same signal as Google Ads — B2B lead-gen usually
  shows weekday peaks, B2C e-commerce evening/weekend peaks.
- **Advantage+ status**: if brief mentions Advantage+ Shopping or
  Sales campaigns, skip scheduling recommendations for those and only
  report observations.

## Data Collection (MCP Tools)

1. `get_meta_hourly_performance` — primary data source; returns per
   campaign × day-of-week (derived from date) × hour rows
2. `get_meta_campaign_performance` — for account-level baseline
   averages over the same range

## Statistical Significance Filter

Same rigor rules as the Google dayparting skill:

- **Minimum bucket volume**: ≥ 100 impressions AND ≥ 1 click per
  (day, hour) bucket across the full date range
- **Minimum conversions for CPA/ROAS claims**: ≥ 3 conversions per
  bucket; below that → directional only
- **Significance threshold**: ≥ 20% off account average

Label buckets: **High performer / Underperformer / Neutral /
Insufficient data**.

## Recommendation Logic

### Ad-set schedule (exclusion)
Only applicable to **ad sets running on Lifetime Budget**:
- Identify consecutive-hour blocks of underperformance
- Recommend excluding those hours via the ad-set schedule editor
- Provide the Facebook Ads Manager click-path since no API-driven
  schedule-writes are supported here

### Ad-set bid adjustments
Meta no longer supports hour-of-day bid adjustments directly — only
ad-set-level daily budgets. If the performance issue is systematic,
recommend:
- Reducing the ad-set budget on low-performance days
- OR splitting the ad set into a "peak-hours" duplicate with higher
  budget and a "off-hours" original with reduced budget

### Advantage+ caveat
If the campaign is Advantage+ (detect via `campaign.name` containing
"Advantage" or objective `OUTCOME_SALES` with Advantage+ enabled —
best-effort; the MCP tool doesn't expose the bit directly):
- Explicitly skip scheduling recommendations
- Report the underperforming windows as an observation only
- Suggest reviewing the campaign's **Advantage+ Shopping expansions**
  settings if evening peak is unusually weak (creative targeting
  might be over-constrained)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-meta-dayparting/`:

- `META-DAYPARTING-REPORT.md` — primary report (with SCORE header)
- `META-DAYPARTING-HEATMAP.md` — 7×24 grid per campaign
- `META-DAYPARTING-RECOMMENDATIONS.md` — specific ad-set-level changes

First non-empty line of `META-DAYPARTING-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: meta_ads PERIOD: <start>..<end> METRIC: <primary_metric>
```

### Report Structure

1. **Heatmap Summary** — 7×24 grid of primary metric, account-level
   and top-3 campaigns
2. **High / Low Performer Blocks** — contiguous day-hour blocks
3. **Advantage+ Observations** — read-only findings for Advantage+
   campaigns (no recommendations, just context)
4. **Ad-set Scheduling Actions** — for non-Advantage+ lifetime-budget
   ad sets, specific changes with expected savings
5. **Budget-split Alternative** — when direct scheduling isn't
   available, the ad-set duplication approach
6. **Insufficient-Data Blocks** — explicit list, no action

## Hard Rules

- **Never recommend a schedule change on an ad set using Daily
  Budget** — Meta doesn't support it, the recommendation won't apply.
- **Advantage+ campaigns: observation only.** Manual scheduling on
  Advantage+ is impossible; recommending it would waste the client's
  time trying to find a non-existent setting.
- **Time zone caveat is mandatory** when the campaign targets a
  non-Spain geography — the hour labels won't match advertiser-local
  time.
- **Never strip > 40% of total hours** from an ad set — Meta's learning
  phase re-initiates on large schedule changes, which typically costs
  2× daily spend in learning phase before stabilising.
- **When a campaign is Advantage+ Shopping / Sales**, escalate
  underperformance findings to review of the **targeting expansion**
  settings, not the schedule.
