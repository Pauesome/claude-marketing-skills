---
name: ads-pacing-monitor
description: >
  Tactical mid-month spend pacing monitor across Google Ads, Meta Ads, and
  LinkedIn Ads. Projects end-of-month spend at current run rate, flags
  campaigns/accounts over- or under-pacing against monthly targets, and
  calculates the daily-budget adjustments needed to land on target. Different
  from ads-budget-review (which does strategic allocation) — this one
  handles the month-end tactical calibration. Activate when the user says
  "pacing check", "am I on track", "month-end spend", "budget pacing",
  "under-pacing", "over-pacing", or asks for a mid-month spend status.
---

# Ads Pacing Monitor — Spain

Answers the question: **"At today's run rate, where do I land on
month-end spend vs target?"** Produces a per-account, per-campaign
pacing status with specific daily-budget adjustments. Cron-friendly —
ideal for Monday-morning and mid-week checks.

## Required Inputs

- `client_id` (required)
- `monthly_targets` (required) — map of account or campaign → monthly
  target in EUR. Can be per-platform total (e.g.
  `{"google_ads": 5000, "meta_ads": 3000, "linkedin_ads": 1500}`) or
  per-campaign (e.g. `{"Brand — Exact": 1200, "Non-Brand": 2000}`).
  Without this input the skill cannot compute pacing.
- `as_of_date` (optional) — the reference date for "today". Defaults to
  current date. Use `as_of_date` to re-run a historical pacing view.

Fail fast if `monthly_targets` is missing. Generic pacing without a
target is meaningless.

## Client Brief

Read `clients/briefs/<client_id>.md` for:

- **Seasonality**: weight the pacing projection if the client has a
  known seasonal spend curve (e.g. Ferrer-Ponseti front-loads
  December; LeadGenCo back-loads September/January). Plain linear pacing
  misleads in those cases.
- **Pacing philosophy**: some clients want linear daily pacing
  (budget / days_in_month) and flag anything >5% off; others are
  fine with back-loaded pacing if the trajectory is trending toward
  target.
- **Any frozen campaigns**: brief may note a campaign is paused for
  compliance review or creative refresh — don't flag these as
  under-pacing.

If brief is missing, assume linear pacing + flag everything literally.

## Data Collection (MCP Tools, parallel)

Pull MTD (start-of-month to `as_of_date`) for every configured platform:

1. `get_google_ads_campaign_performance` — if `client.google_ads` configured
2. `get_meta_campaign_performance` — if `client.meta_ads` configured
3. `get_linkedin_ads_campaign_performance` — if `client.linkedin_ads` configured

Each call uses the same date range: `[YYYY-MM-01, as_of_date]`.

## Pacing Math

For each account / campaign:

```
days_in_month       = total days in current month
days_elapsed        = days from 1st to as_of_date (inclusive)
days_remaining      = days_in_month − days_elapsed
mtd_spend           = sum of spend from MTD fetch
linear_target_mtd   = monthly_target × (days_elapsed / days_in_month)
pacing_ratio        = mtd_spend / linear_target_mtd
projected_eom_spend = mtd_spend + (avg_daily_spend × days_remaining)
                    where avg_daily_spend = mtd_spend / days_elapsed
projection_delta    = projected_eom_spend − monthly_target
adjustment_needed   = projection_delta / days_remaining
                    (negative = reduce daily budget by this amount)
                    (positive = increase daily budget by this amount)
```

## Status Classification

| Status | Criterion |
|---|---|
| **On track** | `0.95 ≤ pacing_ratio ≤ 1.05` |
| **Over-pacing** | `pacing_ratio > 1.05` |
| **Under-pacing** | `pacing_ratio < 0.95` |
| **Zero spend** | `mtd_spend = 0` and days_elapsed ≥ 2 — critical alert (tracking / billing / disapproval issue) |
| **Over budget already** | `mtd_spend ≥ monthly_target` before month-end — critical |

## Severity

- **Critical**: Zero spend for > 48h, OR already over budget, OR
  projected >20% over target
- **High**: Over-pacing > 15%, OR under-pacing > 20%
- **Medium**: Over-pacing 5–15%, OR under-pacing 5–20%
- **Low**: On track — informational only

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-pacing/`:

- `PACING-REPORT.md` — primary report
- `PACING-TABLE.tsv` — per-account / per-campaign rows with MTD,
  target, projection, adjustment (ready for a sheet)

First non-empty line of `PACING-REPORT.md`:

```
STATUS: <on_track|over|under|critical> CLIENT: <client_id> AS_OF: <date> PROJECTED_EOM: €<amount> TARGET: €<amount>
```

### Report Structure

1. **TL;DR** — one line per platform: status, MTD, projected EOM, delta
2. **Critical Flags** — zero spend, over-budget, >20% projection
3. **Per-campaign Breakdown** — sorted by absolute projection delta
4. **Recommended Adjustments** — exact daily-budget changes to apply,
   grouped by platform, with the rationale
5. **Confidence Caveats** — note if MTD covers < 5 days (low
   projection confidence), or if a seasonality pattern from the brief
   affects the linear assumption

## Hard Rules

- **Never recommend pausing a campaign to control over-pacing without
  confirming with the client first** — pausing loses learning in Smart
  Bidding. Prefer reducing daily budget by 20–50% first.
- **Never recommend scaling budget > 20% in one adjustment** — Smart
  Bidding requires 5–7 days to re-optimize; larger jumps destabilize
  CPA.
- **Zero-spend alerts require a tracking/disapproval diagnosis**, not
  a budget adjustment — route to `google-ads-anomaly-diagnostic` or
  the relevant deep-audit skill.
- **When a campaign is brand-new (< 14 days old), pacing math is
  unreliable** — flag as "learning phase" and skip adjustment
  recommendations.
- **Weekend bias**: if `as_of_date` is a Monday and last MTD day was
  weekend, projection underestimates weekday-heavy accounts — note
  the caveat.
