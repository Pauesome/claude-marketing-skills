---
name: ads-creative-audit
description: >
  Cross-platform creative quality audit for Spanish clients. Detects Meta
  creative fatigue (CTR decline > 20% over 14 days), Andromeda similarity
  risk, LinkedIn Thought Leader adoption, format diversity gaps, and refresh
  cadence violations. Activate when user says "creative audit", "ad creative
  review", "creative fatigue", "creative quality", or asks to review ads visually.
---

# Cross-Platform Creative Audit — Spain

Reads creative performance data from the MCP and scores each active platform's
creative portfolio. Thresholds come from `.claude/references/benchmarks-spain.md`;
format specs come from `.claude/references/platform-specs.md`.

## Required Inputs

- `client_id` — resolved via `list_clients`
- `date_range_start` / `date_range_end` — default 30 days (need ≥ 14 days for
  fatigue detection)
- Fail fast on missing input.

## Data Collection (MCP Tools, parallel)

**Meta:**
1. `get_meta_ad_performance` — per-ad time series (impressions, clicks, CTR)
2. `get_meta_creative_metadata` — object_type / body / title / CTA / image_url
3. `get_meta_creatives_for_analysis` with `top_by=spend` — enriched assets
   with base64 images / video frames for the highest-spend ads (cap 20)

**LinkedIn:**
4. `get_linkedin_ads_creative_performance` — per-creative engagement breakdown

**Google (lightweight):**
5. `get_google_ads_campaign_performance` — no asset-level tool yet; audit
   structural compliance (RSA guidance) against `platform-specs.md` only

## Scoring Weights

```
Format Diversity      25%
Fatigue Signals       25%
Platform Compliance   20%
Refresh Cadence       15%
Volume                15%
```

## Check List (CR-01 … CR-15)

### Meta Creative
- **CR-01** Format diversity ≥ 3 formats active (image, video, carousel,
  collection) — High
- **CR-02** ≥ 5 creatives per ad set — High
- **CR-03** Fatigue: compute CTR for each ad in the first 14 days vs the most
  recent 14 days; flag any ad with spend > €100 whose CTR dropped > 20% — Critical
- **CR-04** Andromeda diversity: review top-20 enriched creatives; flag
  accounts whose visual / concept overlap suggests > 60% similarity (same hook,
  same product shot, same layout with colour swaps) — High
- **CR-05** Hook within first 1–3 s (video frames from enriched creatives) — High
- **CR-06** UGC / testimonial content tested — Medium
- **CR-07** Headline ≤ 40 chars, primary text ≤ 125 chars (inspect metadata) — Medium
- **CR-08** Refresh cadence 14–21 days on high-spend ad sets — High
- **CR-09** Captions / subtitles present on videos — Medium
- **CR-10** Advantage+ Creative enhancements enabled — Medium

### LinkedIn Creative
- **CR-11** Thought Leader Ads share ≥ 30% of LinkedIn budget — High
- **CR-12** ≥ 2 formats tested (single image, carousel, video, document) — High
- **CR-13** Creative refresh 4–6 weeks; flag creatives > 6 weeks with
  engagement_rate declining — Medium

### Google Creative
- **CR-14** RSA: ≥ 8 headlines, ≥ 3 descriptions, Ad Strength ≥ "Good" — High
- **CR-15** Extensions: Sitelinks ≥ 4, Callouts ≥ 4, Structured snippets, Image — Medium

## Cross-Platform Synthesis

After scoring each platform individually, produce a synthesis:

- **Volume gap** — which platform is under-creative-ed given spend?
- **Format gap** — which formats are missing per platform (reference the
  Format Diversity Matrix in `platform-specs.md`)
- **Fatigue risk** — list creatives past their refresh cadence sorted by spend
- **Production priority list** — next 5 creatives to produce, ranked by expected
  impact (fatigue replacement first, then format gaps, then Andromeda diversity)

## Fatigue Detection Algorithm

For each Meta ad with spend > €100 in the period:

```
ctr_early  = (clicks first 14 days) / (impressions first 14 days)
ctr_recent = (clicks last 14 days)  / (impressions last 14 days)

IF ctr_early > 0 AND (ctr_early - ctr_recent) / ctr_early > 0.20
  → flag as FATIGUED
```

Supporting signals (flag if any are true):
- Frequency > 5 (prospecting) or > 12 (retargeting)
- Impression volume flat or declining week-over-week despite unchanged budget
- Ad age > 21 days on high-spend ad set

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-creative-audit/CREATIVE-AUDIT-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> SCOPE: creative PERIOD: <start>..<end>
```

Sections:
1. Per-platform score bars
2. **Fatigue alerts** — table of fatigued creatives with creative_id, spend,
   CTR trend, recommended action
3. **Format diversity gaps** per platform
4. **Andromeda similarity assessment** (Meta)
5. **Production priority list** — ranked next 5 creatives to produce
6. Quick Wins (format conversions, CTA changes, caption additions)

## Non-Negotiables

- Never flag fatigue without actual time-series data — if a creative has
  < €100 spend in the period, skip it (insufficient data)
- Reference `platform-specs.md` for format dimensions — never invent specs
- Weight fatigue Critical, Andromeda diversity High — these drive most Meta decline
