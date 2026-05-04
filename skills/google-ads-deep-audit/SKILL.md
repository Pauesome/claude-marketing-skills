---
name: google-ads-deep-audit
description: >
  Deep Google Ads audit for Spanish clients across Search, Performance Max,
  Demand Gen, and Shopping. Evaluates conversion tracking, wasted spend,
  account structure, keywords, Quality Score, ads, and settings against Spain
  benchmarks. Activate when the user says "audit my Google Ads", "Google PPC
  audit", "PMax review", "search ads audit", or references a specific Spanish
  Google Ads client by id.
---

# Google Ads Deep Audit — Spain

Systematic 80-check review of a Google Ads account using MCP tools. All
thresholds come from `.claude/references/benchmarks-spain.md`. All compliance
language comes from `.claude/references/compliance-eu-spain.md`.

## Required Inputs

- `client_id` (required) — confirm via `list_clients`
- `date_range_start` / `date_range_end` — default last 30 days, must cover ≥ 30 days
- No mid-audit prompts; fail fast if inputs missing.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. If the file exists,
use it to contextualise every finding: sector benchmarks, business model (B2B/B2C/
e-commerce/lead-gen), product sensitivity (financial services → Special Ad Category
rules apply; healthcare → LOPDGDD Art. 9 data-sensitivity note), and any
client-specific caveats. If missing, proceed with generic benchmarks and include a
note: "No client brief found — audit uses generic Spain benchmarks."

## Data Collection (MCP Tools)

Run these in parallel:

1. `get_google_ads_campaign_performance` — campaign × day metrics for the period
2. `get_google_ads_search_terms` — include `zero_conversions_only=true` and
   `min_spend=10` to surface wasted-spend terms
3. `get_google_ads_keywords` — returns QS distribution and per-keyword metrics
4. `get_google_ads_impression_share` — budget-lost vs rank-lost IS

Additional context (optional, call if the client has them configured):
- `get_ga_conversion_performance` — verify GA4 conversions align with Google Ads conv actions
- `get_gtm_tags` + `get_gtm_triggers` — confirm gtag / Enhanced Conversions / Consent Mode v2 firing

Before analysing:
- Deduplicate keywords by `(ad_group_id + keyword_text + match_type)`
- Only analyse ENABLED campaigns and ad groups
- Flag wasted spend only on terms with **≥ €10 spend AND 0 conversions**

## Audit Categories & Weights

| Category | Weight | Primary data source |
|---|---|---|
| Conversion Tracking | 25% | GA4, GTM, conversion actions from campaign perf |
| Wasted Spend / Negatives | 20% | `get_google_ads_search_terms` |
| Account Structure | 15% | campaign perf, campaign_type distribution |
| Keywords & Quality Score | 15% | `get_google_ads_keywords` |
| Ads & Assets | 15% | campaign perf, RSA ad strength if available |
| Settings & Targeting | 10% | campaign perf status, bid strategy |

## Critical Checks (severity × 5.0)

Evaluate these first — failure here dominates the score:

- **GA-CT1** gtag / Google Tag firing on all pages (via GTM tags)
- **GA-CT2** Enhanced Conversions active
- **GA-CT3** Consent Mode v2 advanced mode (EEA / UK traffic)
- **GA-CT4** Conversion actions defined, no duplicate counting between GA4 import + native
- **GA-WS1** Search Terms Report reviewed within last 14 days (implicit — if this skill runs it is reviewed)
- **GA-WS2** Negative keyword lists, ≥ 3 themed (Informacional, Empleo, Competencia, Gratis/Pirata)
- **GA-WS3** Wasted spend on irrelevant terms < 5% of total
- **GA-WS4** No BROAD match keywords on Manual CPC (legacy BMM heuristic — flag as FAIL)
- **GA-S1** Brand vs non-brand separated into distinct campaigns
- **GA-S2** Target CPA / ROAS within 20% of historical

## Full Check List

### Conversion Tracking (25%)
- GA-CT5 Offline conversion import configured for lead-gen clients
- GA-CT6 Server-side tagging via GTM Server-Side (recommended)
- GA-CT7 Attribution model: data-driven (rule-based models deprecated)
- GA-CT8 Conversion lag analysis — conversions still trickling in?
- GA-CT9 CAPI equivalent: Enhanced Conversions active with hashed first-party data
- GA-CT10 GA4 conversions imported cross-checked against native Google Ads conversions (no double counting)

### Wasted Spend (20%)
- GA-WS5 Display placement exclusions applied (low-quality sites)
- GA-WS6 Invalid click rate < 5%
- GA-WS7 Broad Match only used with Smart Bidding (tCPA/tROAS/MaxConv)
- GA-WS8 Geographic targeting uses **Presence**, not **Presence or Interest**
- GA-WS9 Negative keywords aren't over-blocking converting queries
- GA-WS10 Shared negative lists exist at account level (not just per campaign)

### Account Structure (15%)
- GA-ST1 Campaign naming consistent and descriptive
- GA-ST2 Ad groups tightly themed (≤ 15–20 keywords)
- GA-ST3 Each RSA ad group has ≥ 3 active ads
- GA-ST4 PMax asset groups structured correctly (text + image + video + signals)
- GA-ST5 SKAG legacy structures migrated to themed groups
- GA-ST6 Paused vs enabled ratio reasonable (< 40% paused)

### Keywords & Quality Score (15%)
- GA-KW1 Match-type distribution appropriate (Exact → Phrase → Broad progression)
- GA-KW2 Weighted avg QS ≥ 7 (check against `quality_score_distribution` in MCP response)
- GA-KW3 Keywords with QS < 5 flagged (FAIL), QS 5–6 (WARNING)
- GA-KW4 No keyword cannibalisation (same term bid in > 1 campaign)
- GA-KW5 Impression share tracked for top spending keywords
- GA-KW6 Bid adjustments set per device / location / audience

### Ads & Assets (15%)
- GA-AD1 RSA: ≥ 8 unique headlines, ≥ 3 descriptions
- GA-AD2 RSA Ad Strength ≥ "Good"
- GA-AD3 Pin usage minimal and strategic
- GA-AD4 Sitelinks ≥ 4, Callouts ≥ 4, Structured snippets present, Image extensions
- GA-AD5 Ad copy includes CTA + value proposition + differentiator
- GA-AD6 Dynamic keyword insertion used appropriately (not in every headline)

### PMax (if present)
- GA-PM1 Audience signals configured per asset group (custom segments, customer lists)
- GA-PM2 PMax Ad Strength ≥ "Good"
- GA-PM3 Brand cannibalisation < 15% from brand terms (use search categories from Insights)
- GA-PM4 Search themes configured (up to 50 per asset group)
- GA-PM5 Campaign-level negative keywords applied
- GA-PM6 PMax not using ECPC (deprecated)
- GA-PM7 Asset group completeness: ≥ 5 images, ≥ 2 logos, ≥ 1 video
- GA-PM8 Video in all required aspect ratios (16:9, 1:1, 9:16)
- GA-PM9 Final URL expansion configured intentionally (opt-out of irrelevant pages)
- GA-PM10 Brand exclusions applied

### Settings (10%)
- GA-SET1 No campaigns still using ECPC (deprecated March 2025 — FAIL if present)
- GA-SET2 Bid strategy appropriate for campaign maturity + goals
- GA-SET3 No campaigns limited by budget (unless intentional)
- GA-SET4 Ad schedule aligned with business hours + conversion patterns
- GA-SET5 Search Partners reviewed; Display opt-out for Search
- GA-SET6 Location targeting refined to Spain (+ specific CCAA where relevant)

### AI Max / Demand Gen (if present)
- GA-AI1 Demand Gen: video + image mix present (20% more conversions combined)
- GA-AI2 Demand Gen: frequency capping monitored manually (native capping absent)
- GA-AI3 Any legacy Video Action Campaigns flagged (deprecated April 2026)
- GA-AI4 CTV campaigns: not using Floodlight (Floodlight does not fire on CTV)

## Scoring

Map each check → PASS / WARNING / FAIL. PASS = full, WARNING = 50%, FAIL = 0%.
Apply severity multiplier × weight × pass-credit, then normalize each category
to 100.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-google-audit/GOOGLE-ADS-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: google_ads PERIOD: <start>..<end>
```

Then sections:

1. Score breakdown (bar chart per category)
2. Critical findings (severity × 5.0 failures) — each with check ID, evidence
   (MCP tool + value), recommendation
3. All other findings grouped by category
4. **Wasted spend estimate** in EUR/month (sum of `wasted_spend` from search
   terms tool)
5. **Quick Wins** — sorted by `severity × impact`
6. **Keyword health matrix** — QS bucket × match-type × spend × conversions
7. **PMax-specific recommendations** if any PMax campaigns exist

## Non-Negotiables

- Every threshold must reference `benchmarks-spain.md` (no inline US figures)
- Wasted-spend flagging requires `spend ≥ €10` AND `conversions = 0`
- Never recommend Broad Match without confirming Smart Bidding is active
- Never recommend BROAD-match negative keywords — default to Exact `[término]`
  or Phrase `"término"`
- Weight ROAS / CPA above rate metrics when multiple metrics disagree
