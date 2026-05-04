---
name: hubspot-funnel-audit
description: >
  Deep HubSpot funnel audit for Spanish clients. Evaluates stage conversion
  rates, cohort integrity (non-retroactive by default), pipeline velocity,
  stalled deals, and weighted pipeline forecast using the client's per-client
  stage_markers config. Activate when the user says "hubspot funnel audit",
  "funnel health", "pipeline audit", "CRM funnel review", "why are leads
  dropping", or asks for a deep dive into HubSpot deal progression.
---

# HubSpot Funnel Audit — Spain

Systematic review of a client's HubSpot funnel driven entirely by the
per-client config in `clients/<client_id>.json` under `hubspot.pipelines[]`
and `hubspot.stage_markers[]`. No client-specific logic lives in this skill —
if it runs on SaaSCo (contact-centred) vs LeadGenCo (deal-centred, boolean
stage markers), the output adapts automatically.

## Required Inputs

- `client_id` (required) — confirm via `list_clients`
- `pipeline` (optional) — pipeline key from client config. Defaults to `is_default: true`.
- `date_range_start` / `date_range_end` — default last 90 days (funnel
  analysis needs a longer window than ad audits)
- No mid-audit prompts; fail fast if inputs missing.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to
interpret the funnel: business model (B2B SaaS vs real-estate lead-gen vs
D2C e-commerce), sales cycle length, and what "conversion" means for this
client. A 14-day B2B cycle is healthy; a 120-day LeadGenCo cycle from Lead to
Mandato Firmado is also healthy — sector determines the benchmark.

## Tool Selection: Funnel vs Cohort Funnel

The two funnel tools answer **different questions** and fetch different
row sets. Picking the wrong one produces misleading numbers.

| Question | Tool | What it counts |
|---|---|---|
| "Of the leads **created in April**, how many are currently prequalified / qualified / etc?" | `get_hubspot_funnel` | Deals **created in the range**, evaluated against each marker right now |
| "How many deals **transitioned into** prequalified (etc.) **in April**, regardless of when the deal was created?" | `get_hubspot_cohort_funnel` with `granularity: "month"` | Every deal whose `marker.date_property` falls in the range, bucketed by its own transition date |

**Key implication for long-cycle clients** (LeadGenCo: ~120d lead → mandato):
a deal created in January may not hit mandato until April. `get_hubspot_funnel`
on April **misses it entirely** (deal wasn't created in April).
`get_hubspot_cohort_funnel` counts it in April's mandato bucket (correct —
that's when the transition happened).

**Default for monthly / weekly performance reports:** use
`get_hubspot_cohort_funnel` (period-activity view).

**Default for cohort retention analysis** ("does January's lead cohort
progress well?"): use `get_hubspot_funnel` with the date range set to
the cohort month.

Always run **both** during an audit — their divergence is itself a signal
(a big gap means lots of in-flight deals created before the period are
converting inside the period).

## Data Collection (MCP Tools, parallel)

1. `get_hubspot_funnel` — core funnel counts + CVRs + median/p90 days between stages
2. `get_hubspot_cohort_funnel` with `granularity: "month"`, `cohort_by: "per_marker"` — non-retroactive cohort view
3. `get_hubspot_cohort_funnel` with `cohort_by: "entry_date"` — retroactive view for comparison
4. `get_hubspot_pipeline_velocity` — median/p90 stage transitions + stalled deals list
5. `get_hubspot_deal_forecast` — weighted pipeline value + next-30-day forecast
6. `get_hubspot_funnel` with `group_by: "utm_source_normalized"` — funnel by source
7. `get_hubspot_funnel` with `group_by: "utm_campaign_canonical"` — funnel by canonical campaign (when campaign_aliases configured)

## Audit Dimensions & Weights

| Dimension | Weight | Primary data source |
|---|---|---|
| Stage Conversion Health | 30% | `get_hubspot_funnel` stages |
| Cohort Integrity | 20% | `get_hubspot_cohort_funnel` (per_marker vs entry_date) |
| Velocity & Stalled Deals | 20% | `get_hubspot_pipeline_velocity` |
| Source / Campaign Funnel Variance | 15% | `get_hubspot_funnel` group_by |
| Forecast & Weighted Pipeline | 15% | `get_hubspot_deal_forecast` |

## Critical Checks (severity × 3.0)

- **HF-CT1** Pipeline has `stage_markers[]` configured in client config (else skill cannot run — emit missing-config error)
- **HF-CT2** Top-of-funnel stage count > 0 in the period (else no data to audit)
- **HF-CT3** Every stage marker has a `date_property` set (required for cohort bucketing and velocity)
- **HF-CT4** At least one stage has `probability = 1.0` (won marker) — required for revenue attribution in source/campaign tools
- **HF-CT5** Cohort non-retroactive view is enabled (`cohort_rules.retroactive = false`) — prevents Apr demos from being backfilled into Jan

## Full Check List

### Stage Conversion Health (30%)
- **HF-SC1** Stage CVR from previous stage ≥ sector benchmark (check brief for benchmark). Flag FAIL if any stage < 50% of prior CVR without explanation.
- **HF-SC2** No "dead stage" (count = 0 for > 30 days) unless intentionally abandoned
- **HF-SC3** Final-stage CVR from top-of-funnel documented — this is the effective lead → customer rate
- **HF-SC4** Counts strictly decreasing from top to bottom (else stage_markers logic is broken)
- **HF-SC5** Revenue per won deal ≥ client's expected AOV / ACV from brief

### Cohort Integrity (20%)
- **HF-CI1** Per-marker view (non-retroactive) is the primary view for MoM trending
- **HF-CI2** Lead-month vs demo-month divergence analysed (Jan leads → Apr demos is normal — don't backfill)
- **HF-CI3** Retroactive view compared to per-marker to measure in-flight deal backlog
- **HF-CI4** Cohort trend shows month-over-month improvement or flagged decline
- **HF-CI5** Each cohort has adequate sample size (≥ 20 rows) — else emit low-confidence warning
- **HF-CI6** `get_hubspot_cohort_funnel` row count > `get_hubspot_funnel` for the same period and marker implies in-flight backlog converting — documented in the report, not flagged as inconsistency
- **HF-CI7** `warnings[]` on cohort response inspected — any "skipped N rows" warning means the client's stage marker matches a row without a date_property value; document and recommend either tightening the matcher (use `all_of` with `property_exists` on the date_property) or populating the missing field

### Velocity & Stalled Deals (20%)
- **HF-VE1** Median days per stage ≤ benchmark for the sector
- **HF-VE2** p90 days per stage ≤ 2× median (else long-tail investigation)
- **HF-VE3** Stalled deal count ≤ 10% of active pipeline
- **HF-VE4** Top-10 stalled deals reviewed (list included in report)
- **HF-VE5** Stage velocity consistent across sources (no source is systematically slower)

### Source / Campaign Funnel Variance (15%)
- **HF-SC1** Paid vs organic CVR compared (organic should usually convert better — paid brings volume)
- **HF-SC2** Per-canonical-campaign CVR visible (requires `campaign_aliases` config)
- **HF-SC3** Source mix visible and labelled (no > 30% of leads tagged `offline` / `-` / `null` — else UTM hygiene issue)
- **HF-SC4** Google vs Meta vs LinkedIn funnel CVR documented separately

### Forecast & Weighted Pipeline (15%)
- **HF-FC1** Every open-stage marker has a `probability` set
- **HF-FC2** `weighted_pipeline_value` reasonable vs historical won revenue
- **HF-FC3** `forecast_next_30d` ≤ `weighted_pipeline_value` (sanity check)
- **HF-FC4** Open deals by stage in a pyramid shape (most at bottom of open funnel, fewest near won) — inverted pyramid = bottleneck
- **HF-FC5** Forecast confidence band communicated (≥ 12 historical months recommended for reliable probabilities)

## Scoring

Each check → PASS / WARNING / FAIL. PASS = full credit, WARNING = 50%,
FAIL = 0%. Critical checks × 3.0 multiplier. Normalize each dimension to
100 then weighted average → overall score.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-hubspot-funnel-audit/`:

- `HUBSPOT-FUNNEL-REPORT.md` — comprehensive findings
- `HUBSPOT-STALLED-DEALS.md` — top stalled deals with deal_id, stage, days, amount
- `HUBSPOT-FORECAST.md` — weighted pipeline table + 30-day forecast

First non-empty line of `HUBSPOT-FUNNEL-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: hubspot PERIOD: <start>..<end>
```

Then sections:

1. **Funnel Snapshot** — stage table with count, CVR from prev, CVR from top, median days, p90 days
2. **Cohort Trend** — per-marker bucket table for last 6 months
3. **Velocity Breakdown** — stage-to-stage transitions with median/p90 + stalled counts
4. **Source Funnel** — CVR by normalized source; flag sources < 50% of average CVR
5. **Campaign Funnel** — CVR by canonical campaign (if aliases configured, else note)
6. **Forecast** — weighted pipeline value + forecast-next-30d with stage breakdown
7. **Quick Wins** — issues fixable in < 1 hour with estimated impact
8. **Action List** — Critical → High → Medium → Low, each with check ID + recommendation

## Non-Negotiables

- Every threshold must come from `clients/briefs/<client_id>.md` context or
  generic SaaS/e-commerce/lead-gen defaults — not hardcoded numbers in this
  skill
- Default cohort view is **per_marker** (non-retroactive) — only use
  entry_date for diagnostic comparison
- Never recommend changes that would require retroactive cohort recalculation
  without explicit user confirmation
- Weight revenue-bearing stages (prob > 0.5) above top-of-funnel stages when
  conflicting findings surface
- If the pipeline has `stage_markers: []` (e.g. LeadGenCo Demand), emit
  "pipeline not configured" and exit without scoring
