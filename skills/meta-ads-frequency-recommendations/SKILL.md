---
name: meta-ads-frequency-recommendations
description: >
  Analyse Meta Ads frequency (impressions per unique reach) and correlate
  with conversion rate to recommend frequency caps per campaign objective.
  Identifies the inflection point where additional impressions stop driving
  conversions and start burning budget on overexposure. Meta-specific —
  complements meta-ads-deep-audit's creative fatigue findings with a concrete
  cap number. Activate when the user says "frequency cap", "audience
  saturation", "frequency too high", "overserving ads", "frequency
  recommendations", or asks how often the same person should see an ad.
---

# Meta Ads Frequency Recommendations — Spain

Uses aggregate campaign frequency (computed as `impressions / reach`)
correlated with conversion rate to recommend a frequency cap per
campaign objective. Prospecting, Retargeting, and Brand campaigns each
have different healthy frequency curves.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 60 days
  (need enough volume to see the frequency → conversion curve;
  shorter windows are noisy)
- `campaign_ids` (optional) — scope to specific campaigns

## Client Brief

Read `clients/briefs/<client_id>.md`:

- **Audience size**: small audiences saturate faster. If the brief
  mentions a niche audience (< 500k), expect higher baseline
  frequency and earlier saturation.
- **Creative refresh cadence**: if brief mentions creatives refresh
  weekly, frequency tolerance is higher (same person seeing different
  ads doesn't burn out). If creatives rotate monthly, saturation
  hits sooner.
- **Campaign objective mix**: Prospecting vs Retargeting vs Brand
  campaigns need different caps. Brief should clarify which is which;
  if unclear, infer from campaign names (contains "retarget",
  "remarket" → retargeting; "prospect", "awareness", "broad" →
  prospecting).

## Data Collection (MCP Tools)

1. `get_meta_campaign_performance` — returns impressions, reach,
   conversions, spend per campaign. Frequency is derived client-side
   as `impressions / reach`.
2. `get_meta_hourly_performance` — used to compute directional
   frequency-by-day trends if the single aggregate frequency value is
   uninformative (e.g. for very long date ranges where the frequency
   fluctuates materially).

If reach is zero or missing, frequency cannot be computed — flag the
campaign as "frequency data unavailable" and skip it.

## Classification by Objective

Infer the objective from campaign name patterns (case-insensitive):

| Objective | Name patterns | Baseline healthy frequency (per 7 days) |
|---|---|---|
| **Prospecting** | "prospect", "broad", "awareness", "TOF", "top-of-funnel" | 1.5–2.5 |
| **Retargeting** | "retarget", "remarket", "RT", "warm", "website-visitors" | 3.0–5.0 |
| **Brand / Always-On** | "brand", "always-on", "evergreen" | 2.0–3.5 |
| **Unknown** | anything else | Treat as Prospecting baseline |

These are starting points — real recommendations come from the
conversion-rate curve, not from generic baselines.

## Frequency vs Conversion Rate Analysis

For each campaign:

1. Compute aggregate frequency = `impressions / reach` (total, not
   per-day)
2. Compute conversion rate = `conversions / clicks`
3. Compare against:
   - The campaign's historical frequency (previous 60-day window)
   - Other campaigns of the same objective class for the same client

Flag as **over-frequency** when:
- Aggregate frequency > 2× the objective baseline (e.g. prospecting
  at 5.0+, retargeting at 10.0+)
- AND conversion rate dropped ≥ 20% vs previous period (diminishing
  returns signal)
- AND the campaign has spent ≥ €100 in the period (volume threshold)

Flag as **healthy** when:
- Frequency within 1.5× baseline
- Conversion rate stable or growing

## Recommendation Logic

### Frequency cap recommendation

For over-frequency campaigns, recommend:

- **Prospecting**: cap at 3 per 7 days (Meta's default cap interface)
- **Retargeting**: cap at 5 per 7 days
- **Brand / Always-On**: cap at 4 per 7 days

Explain that these are starting points; the actual inflection point
would need the Meta Insights `frequency_value` breakdown (not
currently available via our MCP).

### Creative refresh (alternative to cap)

If creative age > 28 days AND frequency is high, recommend creative
refresh *before* applying a frequency cap — fresh creative extends
the useful frequency range more effectively than capping does.

### Audience expansion

If a Prospecting campaign hits 5+ frequency with a small audience
(< 500k) AND conversions are positive, recommend **audience
expansion** rather than frequency cap — more people to show it to,
not fewer impressions to the same people.

## Savings Estimate

For each over-frequency campaign:

```
wasted_spend_estimate = impressions_above_baseline_freq × cpm / 1000
```

Where `impressions_above_baseline_freq` = impressions that the cap
would have prevented. Approximate: if current freq is 5 and cap is 3,
assume 40% of impressions above the cap; scale to verify this figure
is monthly.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-meta-frequency/`:

- `META-FREQUENCY-REPORT.md` — primary report (with SCORE header)
- `META-FREQUENCY-CAMPAIGNS.tsv` — per-campaign rows: objective,
  freq, conv_rate, recommendation

First non-empty line of `META-FREQUENCY-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: meta_ads PERIOD: <start>..<end> OVER_FREQ_CAMPAIGNS: <count>
```

### Report Structure

1. **Summary** — count of over-frequency campaigns, estimated
   wasted spend, recommended actions
2. **Per-Campaign Analysis** — each over-frequency campaign with
   objective, current freq, conv-rate trend, recommendation
   (cap / refresh / expand)
3. **Healthy Campaigns** — brief list of campaigns in healthy range
   (informational, not actionable)
4. **Methodology Caveats** — explicitly note that this analysis uses
   aggregate frequency (`impressions / reach`) and cannot isolate the
   exact inflection point. For precise curve analysis, the Meta
   Insights `frequency_value` breakdown would be required.

## Hard Rules

- **Never recommend a frequency cap on a campaign with < €100 spend
  in the period** — not enough signal.
- **Always prefer creative refresh over a cap on young campaigns**
  (< 14 days) — low frequency is expected in learning phase; the
  real issue will be creative fatigue in 3–4 weeks.
- **Never apply a cap to a campaign that's actively scaling** (spend
  trend up + CPA stable) — caps constrain reach and can abort the
  scaling run.
- **Audience size + frequency together** drive the recommendation —
  a high freq on a small audience is **audience expansion**, not a
  cap.
- **Caveat the precision**: aggregate-level frequency analysis is
  directionally useful, not surgically precise. The report must state
  this explicitly so the operator doesn't trust the numbers more
  than they deserve.
