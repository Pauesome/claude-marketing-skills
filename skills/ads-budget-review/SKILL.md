---
name: ads-budget-review
description: >
  Budget allocation and bidding strategy review across Google, Meta, and
  LinkedIn for Spanish clients. Applies the 70/20/10 rule, 3× Kill Rule, and
  20% Scaling Rule; produces a kill list and scale list. Activate when the
  user says "budget review", "budget allocation", "bidding strategy", "scale
  my ads", "kill list", "ROAS target", or asks about ad spend efficiency.
---

# Budget & Bidding Review — Spain

All thresholds come from `.claude/references/benchmarks-spain.md`.

## Required Inputs

- `client_id` — resolved via `list_clients`
- `date_range_start` / `date_range_end` — default last 14 days; minimum 14 for
  kill/scale decisions.
- Fail fast on missing input.

## Data Collection

Pull in parallel (only for platforms the client has configured):

1. `get_cross_channel_summary` — totals, by_platform spend_share, top campaigns
2. `get_google_ads_campaign_performance` — campaign-level spend, CPA, ROAS, bid strategy
3. `get_google_ads_impression_share` — budget-lost IS for scale decisions
4. `get_meta_campaign_performance` — campaign spend, CPA, ROAS
5. `get_linkedin_ads_campaign_performance` — spend, CPA, frequency

Attribute revenue via:
- `get_hubspot_deals` filtered by utm_source per platform
- `get_ga_channel_performance` for Paid Search / Paid Social cross-check

## Framework

### 70 / 20 / 10 Rule
- 70% Proven — platforms hitting ROAS/CPA target for ≥ 14 days
- 20% Scaling — platforms showing promise, need more data
- 10% Testing — new platforms or strategies

### Platform Selection Matrix

| Business type | Primary | Secondary | Testing |
|---|---|---|---|
| SaaS B2B | Google Search, LinkedIn | Meta | YouTube |
| E-commerce | Google Shopping, Meta | YouTube | LinkedIn |
| Local Service (Spain) | Google Search, Google LSA | Meta | YouTube |
| B2B Enterprise | LinkedIn, Google Search | Meta | — |
| Info Products | Meta, YouTube | Google Search | — |
| Automotive (Walcu clients) | Google Search, Meta | YouTube | LinkedIn |
| Wellness / Salud | Google Search | Meta | YouTube |

Detect business type from HubSpot pipeline / GA4 content patterns; ask the
user only if truly ambiguous (otherwise pick best guess and flag it in output).

### Budget Sufficiency (EUR/day)

Refer to `benchmarks-spain.md` for thresholds. Flag any campaign below the
platform minimum as **Critical** — learning phase cannot exit.

## Bidding Strategy Decision Trees

### Google
```
<30 conv/mo        → Maximize Clicks (cap at avg CPC benchmark)
30–50 conv/mo      → Maximize Conversions
>50 conv/mo        → Target CPA
>50 + revenue tag  → Target ROAS
```
- Flag any campaign still on **ECPC** (deprecated March 2025) — FAIL.

### Meta
- Lowest Cost (default) — volume; CPA variance acceptable
- Cost Cap — CPA ceiling; may reduce volume
- Bid Cap — max bid per auction
- ROAS Goal — target ROAS on revenue-tracked campaigns
- CBO vs ABO: CBO for proven, ABO for testing

### LinkedIn
- Manual CPC for early-stage cost control
- Cost Cap once CPA is stable
- Maximum Delivery only at scale — never as default (most expensive option)

## Scaling Assessment

Ready-to-scale criteria (ALL must be true):
- CPA < target for 2+ weeks
- ≥ 50 conversions / week (learning exited)
- CTR stable or improving
- ROAS above target
- No creative fatigue (cross-reference `ads-creative-audit` findings if
  available in `./reports/<client_id>/`)

Scaling method — **20% Rule**: `new_budget = old_budget × 1.20`, wait 3–5 days.

## Kill List Rules

| Scenario | Data gate | Action |
|---|---|---|
| CPA > 3× target | ≥ 7 days AND ≥ 20 clicks | Pause |
| No conversions | ≥ €80 spend OR ≥ 50 clicks | Pause + diagnose |
| CTR < 50% benchmark | ≥ 1 000 impressions | Kill creative, replace |
| ROAS < 50% target | ≥ 14 days | Cut budget 50% or pause |

Never list a kill candidate that hasn't met its data gate.

## Score Components

| Component | Weight |
|---|---|
| Allocation Strategy (70/20/10) | 25% |
| Bidding Strategy appropriateness | 25% |
| Scaling Readiness | 25% |
| Budget Sufficiency | 25% |

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-budget-review/BUDGET-STRATEGY-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> SCOPE: budget PERIOD: <start>..<end>
```

Sections:
1. Current vs recommended allocation (table by platform with % shares)
2. **Bidding strategy per campaign** — current, recommended, reason
3. **Scale list** — campaigns meeting all scale criteria, with +20% target
4. **Kill list** — campaigns meeting a kill rule, with data gate evidence
5. **MER (Marketing Efficiency Ratio)** — compute from cross-channel summary
   and HubSpot revenue if available
6. Quick Wins

## Non-Negotiables

- Never recommend increasing budget > +20% at once
- Never list a kill candidate that hasn't met its data gate
- Cite `benchmarks-spain.md` for every threshold
- Weight ROAS above CPA above CTR when metrics disagree
- Flag ECPC-using Google campaigns as FAIL
