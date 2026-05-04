---
name: meta-ads-deep-audit
description: >
  Deep Meta Ads audit for Spanish clients covering Facebook and Instagram.
  Evaluates Pixel/CAPI health, Event Match Quality, Andromeda creative
  diversity, creative fatigue, account structure, and audience targeting.
  Activate when the user says "audit my Meta Ads", "Facebook Ads audit",
  "Instagram audit", "Advantage+ review", or references a Spanish Meta client.
---

# Meta Ads Deep Audit — Spain

Systematic 50-check review of a Meta Ads account using MCP tools. All
thresholds come from `.claude/references/benchmarks-spain.md`.

## Required Inputs

- `client_id` — resolved via `list_clients`
- `date_range_start` / `date_range_end` — default 30 days, min 14 days
- Fail fast on missing input; no mid-audit prompts.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to frame every
finding: business type (B2C/D2C/lead-gen), product category, whether the account
falls under Special Ad Categories (financial, healthcare/wellness), and any brand
tone notes that affect creative scoring. If missing, proceed with generic benchmarks
and note the gap.

## Andromeda Awareness (Oct 2025)

Meta's Andromeda engine clusters creatives with > 60% similarity and suppresses
delivery of near-identical ads. 100 minor variations perform no better than 10
genuinely distinct concepts. Flag any ad set relying on iterative colour /
text swaps instead of distinct concepts.

## Data Collection (MCP Tools, parallel)

1. `get_meta_campaign_performance` — campaign × day
2. `get_meta_ad_performance` — ad-level metrics, includes `reach` and
   `creative_id`
3. `get_meta_creative_metadata` — object_type / title / body / image_url
4. `get_meta_creative_assets_enriched` — for top-spending ads, pull base64
   assets + video frames for visual similarity assessment (cap at 20 ads)

Optional:
- `get_hubspot_deals` — verify lead handoff if client uses Meta Lead Ads
- `get_ga_events` — verify Meta-sourced sessions hit expected conversion events

## Audit Categories & Weights

| Category | Weight |
|---|---|
| Pixel / CAPI Health | 30% |
| Creative (Diversity & Fatigue) | 30% |
| Account Structure | 20% |
| Audience & Targeting | 20% |

## Critical Checks (severity × 5.0)

- **M-PX1** Meta Pixel installed and firing (verify via GTM tags if available)
- **M-PX2** CAPI active (without it: 30–40% post-iOS-14.5 data loss)
- **M-PX3** Event deduplication ≥ 90% (event_id matching)
- **M-PX4** EMQ (Purchase) ≥ 8.0
- **M-CR1** Creative format diversity ≥ 3 formats active
- **M-CR2** Creative fatigue: flag any top-spend creative with CTR declining
  > 20% over the last 14 days (compute from `get_meta_ad_performance` time series)
- **M-ST1** Learning Limited ad sets < 30%

## Full Check List

### Pixel / CAPI Health (30%)
- M-PX5 All standard events configured (ViewContent, AddToCart, Purchase, Lead)
- M-PX6 Custom conversions created for non-standard events
- M-PX7 Aggregated Event Measurement (AEM) configured for iOS
- M-PX8 Domain verification completed
- M-PX9 Server-side events include customer_information parameters (em, ph, fn, ln, ct, st, zp, external_id)
- M-PX10 Pixel fires with correct currency (EUR) and value parameters
- M-PX11 Offline Conversions API not in use (discontinued May 2025 — migrate to CAPI)
- M-PX12 CMP integration active (Cookiebot/OneTrust/Didomi/Funnel/Iubenda — required by Meta EU User Consent Policy)
- M-PX13 Event-level consent state passed on every CAPI event

### Creative — Diversity & Fatigue (30%)
- M-CR3 ≥ 5 creatives per ad set
- M-CR4 Genuinely distinct concepts ≥ 10 across the account (Andromeda diversity)
- M-CR5 Video ≤ 15 s Stories / Reels, ≤ 30 s Feed
- M-CR6 UGC / testimonial creative tested
- M-CR7 Dynamic Creative Optimization (DCO) tested
- M-CR8 Headline ≤ 40 chars, primary text ≤ 125 chars
- M-CR9 Creative refresh cadence every 14–21 days on high-spend ad sets
- M-CR10 Advantage+ Creative enhancements enabled where appropriate
- M-CR11 Captions / subtitles on all video (accessibility + sound-off)
- M-CR12 Hook within first 1–3 seconds (video)

### Account Structure (20%)
- M-ST2 Campaign consolidation: 1–3 campaigns total for simplified structure
- M-ST3 CBO vs ABO choice intentional (CBO for proven, ABO for testing)
- M-ST4 Budget per ad set ≥ 5× target CPA
- M-ST5 Ad set audience overlap < 30% (per Audience Overlap tool)
- M-ST6 Advantage+ Sales Campaigns active for e-commerce with catalog
- M-ST7 Campaign naming consistent
- M-ST8 Exclusions set: purchasers excluded from prospecting, retargeting pools separated

### Audience & Targeting (20%)
- M-AU1 Prospecting 7-d frequency < 3.0
- M-AU2 Retargeting 7-d frequency < 8.0
- M-AU3 Custom Audiences exist: website visitors, customer lists, engagement
- M-AU4 Lookalike Audiences: multiple seed sizes tested (1%, 3%, 5%)
- M-AU5 Advantage+ Audience tested vs manual
- M-AU6 Interest targeting broad enough for algo optimization
- M-AU7 Location targeting: Spain (and CCAA if client requires it) with no
  wasted international spend
- M-AU8 Special Ad Category declared where applicable (housing / employment /
  credit / financial products — see `compliance-eu-spain.md`)

## EMQ Remediation Guide

| EMQ | Action |
|---|---|
| 8.0–10.0 | Maintain |
| 6.0–7.9 | Add more customer_information parameters |
| 4.0–5.9 | Implement CAPI, improve data quality |
| < 4.0 | Critical: CAPI + Enhanced Matching required |

Key parameters in priority order: `em`, `ph`, `fn`, `ln`, `ct`, `st`, `zp`, `external_id`.

## Threads Placement (Jan 2026 GA)

Currently < 0.1% of spend in Spain. Mention only if the client has declared
interest in awareness-layer expansion — do not flag as a core finding.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-meta-audit/META-ADS-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: meta_ads PERIOD: <start>..<end>
```

Sections:
1. Score breakdown
2. **EMQ improvement roadmap** — if any event is below 8.0
3. **Creative fatigue alerts** — list every creative with CTR declining > 20%
4. Per-check findings grouped by category
5. **Andromeda diversity assessment** — distinct concept count + suppression
   risk scoring
6. Quick Wins
7. Advantage+ adoption recommendations

## Non-Negotiables

- All thresholds cite `benchmarks-spain.md`
- No US Special Ad Category handling — use EU rules from `compliance-eu-spain.md`
- Creative fatigue detection requires actual time-series data, not assumptions
- Flag Offline Conversions API as FAIL (discontinued)
- Never recommend narrow audiences without Lookalike / Predictive seed support
