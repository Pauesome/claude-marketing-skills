---
name: hubspot-ads-reconciliation
description: >
  Reconciles paid-ad spend (Google, Meta, LinkedIn) with HubSpot CRM leads
  and revenue, joining by canonical campaign name via the client's
  campaign_aliases config. Surfaces spend-without-leads, leads-without-spend,
  CRM vs ad-platform conversion discrepancies, and true CPL / CPA / ROAS.
  Activate when the user says "reconcile ads with hubspot", "ads vs CRM",
  "does Google Ads match CRM", "platform vs pipeline", "true CPL", or
  "cross-channel revenue".
---

# HubSpot × Ads Reconciliation — Spain

Cross-channel reconciliation audit. Ad platforms report impressions,
clicks, spend, and their own conversions. HubSpot reports actual qualified
leads, won deals, and revenue. These rarely match — this skill explains
why and produces the true funnel.

Join key: **canonical campaign name** — the same rule on both sides.
Ad-platform campaign names are canonical by construction; HubSpot's
`utm_campaign` passes through the client's `campaign_aliases` regex rules
to get canonical.

## Required Inputs

- `client_id` (required) — client must have at least one ad platform + HubSpot configured
- `date_range_start` / `date_range_end` — default last 30 days
- Fail fast on missing input.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to
interpret mismatches: LeadGenCo has many phone-call leads that never carry
UTMs (explains ad spend without attributed CRM leads); SaaSCo has
outbound-sourced demos on leads that originally came from paid (explains
CRM leads without corresponding ad-platform conversions in the last-touch
window).

## Data Collection (MCP Tools, parallel)

1. `get_cross_channel_summary` — authoritative platform × spend × conversions + CRM overlay
2. `get_google_ads_campaign_performance` — Google spend per campaign (already canonical)
3. `get_meta_campaign_performance` — Meta spend per campaign (already canonical)
4. `get_linkedin_ads_campaign_performance` — LinkedIn spend (if configured)
5. `get_hubspot_campaign_performance` — HubSpot revenue per canonical campaign (after alias resolution)
6. `get_hubspot_source_attribution` with `dimension: "utm_campaign"` — raw utm_campaign distribution (to detect aliasing gaps)

## Audit Dimensions & Weights

| Dimension | Weight | Primary data source |
|---|---|---|
| Campaign Alias Resolution | 25% | `get_hubspot_source_attribution` + `campaign_aliases` config |
| Spend-without-Leads | 25% | Cross-channel join; platform row with crm_leads = 0 |
| Leads-without-Spend | 20% | HubSpot row where no ad platform has matching canonical |
| Platform vs CRM Conversion Delta | 20% | Platform `conversions` vs HubSpot `contacts` / `won_deals` |
| True CPL / CPA / ROAS | 10% | Overlayed cross-channel summary |

## Critical Checks (severity × 3.0)

- **HR-CT1** At least one ad platform configured (else nothing to reconcile)
- **HR-CT2** HubSpot configured with `campaign_aliases` for clients where HubSpot utm_campaign differs from ad-platform campaign names (LeadGenCo, Meta-heavy clients)
- **HR-CT3** Top-5 spending campaigns in each ad platform appear in HubSpot under canonical name (else alias map is broken)
- **HR-CT4** At least 50% of HubSpot-reported leads link to an ad-platform campaign (else attribution is lost between click and CRM)
- **HR-CT5** Platform conversion count vs HubSpot contact count within 2× (else pixel/CAPI may be double-counting or failing)

## Full Check List

### Campaign Alias Resolution (25%)
- **HR-AR1** Every Google Ads campaign with spend has ≥ 1 matching HubSpot canonical row
- **HR-AR2** Every Meta campaign with spend has ≥ 1 matching HubSpot canonical row (accounting for adset-name quirk)
- **HR-AR3** Every LinkedIn campaign with spend has ≥ 1 matching HubSpot canonical row
- **HR-AR4** Reverse: every HubSpot canonical with > 5 leads has a matching ad-platform campaign OR is explained (organic, outbound, referral)
- **HR-AR5** List unresolved HubSpot utm_campaign values — recommend new `campaign_aliases` rules

### Spend-without-Leads (25%)
- **HR-SL1** Campaigns with > €100 spend AND 0 HubSpot leads flagged as FAIL
- **HR-SL2** Campaigns with > €500 spend AND < 5 HubSpot leads flagged as WARNING
- **HR-SL3** Root-cause hypothesis per flagged campaign: UTM missing, alias missing, landing page form broken, or genuine waste
- **HR-SL4** Platform-native conversion count compared to CRM lead count — if native ≫ CRM, pixel fires on non-form events
- **HR-SL5** Devices / placements contributing to the spend-no-leads bucket

### Leads-without-Spend (20%)
- **HR-LS1** HubSpot canonicals with ≥ 5 leads and no matching ad platform campaign — explain via organic / outbound / referral
- **HR-LS2** Offline-source leads proportion (from source_normalization = "offline") logged — these are phone calls / walk-ins, not reconciliation failures
- **HR-LS3** Branded-search leads not double-counted as "free" if Brand campaigns exist in Google Ads
- **HR-LS4** Direct traffic leads — if significant, recommend GA4 + HubSpot cross-check

### Platform vs CRM Conversion Delta (20%)
- **HR-CD1** Per-campaign table: platform_conversions, hubspot_contacts, hubspot_won_deals — delta % shown
- **HR-CD2** Flag campaigns where platform_conversions > 2 × hubspot_contacts (pixel over-fires) or < 0.5 × (pixel under-fires)
- **HR-CD3** Conversion definition alignment: platform "lead" = HubSpot contact? or HubSpot open_deal? Check brief for what counts
- **HR-CD4** Attribution window differences noted (Google 30d click / 1d view; Meta 7d/1d; HubSpot = lifetime)

### True CPL / CPA / ROAS (10%)
- **HR-TR1** True CPL (spend / HubSpot contacts) per campaign vs platform-reported CPL
- **HR-TR2** True CPA (spend / HubSpot won_deals) per campaign
- **HR-TR3** True ROAS (HubSpot revenue / spend) per campaign vs platform-reported ROAS
- **HR-TR4** Top-5 campaigns by true ROAS vs top-5 by platform ROAS — flag divergence
- **HR-TR5** Aggregate true MER (HubSpot total revenue / total ad spend)

## Scoring

Each check → PASS / WARNING / FAIL. Critical checks × 3.0. Normalize per
dimension → weighted average → overall score.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-hubspot-ads-reconciliation/`:

- `RECONCILIATION-REPORT.md` — findings + action list
- `RECONCILIATION-MATRIX.md` — per-campaign table (spend × platform_conv × crm_leads × crm_won × revenue × true-CPL × true-CPA × true-ROAS)
- `ALIAS-GAPS.md` — unresolved HubSpot utm_campaign values with recommended regex rules

First non-empty line of `RECONCILIATION-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: cross_channel PERIOD: <start>..<end>
```

Then sections:

1. **Reconciliation Matrix** — per-campaign table joining platform × CRM
2. **Spend Without Leads** — flagged campaigns with root cause hypothesis
3. **Leads Without Spend** — HubSpot canonicals unmatched to paid channels
4. **Conversion Delta** — platform vs CRM conversion mismatches
5. **True Unit Economics** — true CPL / CPA / ROAS per campaign
6. **Recommended Alias Rules** — regex additions to `clients/<id>.json`
7. **Quick Wins** — fixable in < 1 hour
8. **Action List** — Critical → High → Medium → Low

## Non-Negotiables

- True ROAS / CPA from HubSpot ALWAYS overrides platform-reported figures
  when the two disagree
- Never flag spend-without-leads without checking the alias map first (the
  map may simply be missing a rule, not the campaign being wasted)
- Alias-gap recommendations must include the exact regex pattern ready to
  paste into `hubspot.campaign_aliases[]`
- Offline / phone-call leads (source = "offline") are NOT reconciliation
  failures — surface but don't downrank attributed campaigns for it
- Attribution-window differences always noted in the report; never compared
  naively across platforms with different windows
