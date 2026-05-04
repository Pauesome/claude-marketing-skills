---
name: linkedin-ads-deep-audit
description: >
  Deep LinkedIn Ads audit for Spanish B2B clients. Evaluates Insight Tag /
  CAPI, audience targeting, Thought Leader Ads adoption, lead gen form
  friction, and budget/bidding. Uses new Oct 2025 terminology
  (Campaign Group → Campaign → Ad Set). Activate when user says "audit my
  LinkedIn Ads", "B2B ads audit", "sponsored content review", "lead gen
  review", or references a Spanish LinkedIn client.
---

# LinkedIn Ads Deep Audit — Spain

Systematic 27-check review using MCP tools. All thresholds come from
`.claude/references/benchmarks-spain.md`.

**Terminology (Oct 2025 rename):** Campaign Groups → Campaigns, Campaigns → Ad Sets.
EU note: **Sponsored Messaging / InMail / Conversation Ads are discontinued
for EU-targeted campaigns since January 2022.** Never recommend them to
Spanish clients.

## Required Inputs

- `client_id` — resolved via `list_clients`
- `date_range_start` / `date_range_end` — default 30 days
- Fail fast on missing input; no mid-audit prompts.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to anchor the
audit: industry vertical (SaaS, manufacturing, professional services, etc.), ICP
(seniority, function, company size), sales cycle length, and whether LinkedIn is
the primary or secondary channel. These determine whether underperformance is a
targeting problem, a creative problem, or a channel-fit problem. If missing,
proceed with generic B2B Spain benchmarks and note the gap.

## Data Collection (MCP Tools, parallel)

1. `get_linkedin_ads_campaign_performance` — campaign × day
2. `get_linkedin_ads_demographics` — call once per relevant pivot: `job_function`,
   `seniority`, `industry`, `company_size`. Drives L03/L04/L05 scoring.
3. `get_linkedin_ads_creative_performance` — per-creative engagement + CTR
4. `get_linkedin_ads_lead_gen_performance` — form_opens, leads, qualified_leads
5. `get_linkedin_ads_audience_reach` — reach, frequency, audience_penetration_pct
   (cap at 92-day date window — narrow if needed)

Optional:
- `get_hubspot_deals` with `utm_source=linkedin` — closed-loop L23 (lead-to-opp)
- `get_gtm_tags` — verify Insight Tag and CAPI firing

## Audit Categories & Weights

| Category | Weight |
|---|---|
| Technical Setup | 25% |
| Audience Targeting | 25% |
| Creative Quality | 20% |
| Lead Gen & Performance | 15% |
| Bidding & Budget | 15% |

## Checks

### Technical Setup (25%)
- L01 Insight Tag installed and firing on all pages (Critical)
- L02 Conversions API (CAPI) active — launched 2025 (High)
- L03 Conversion events configured for full funnel (content view, form start,
  form submit, MQL qualification) (High)
- L04 Revenue attribution tracking enabled where client has revenue events (Medium)
- L05 Salesforce / HubSpot CRM integration active (June 2025) — closed-loop
  impression-to-revenue reporting (High)
- L06 Consent Mode v2 active (Microsoft-owned — same stack as Bing) (High)

### Audience Targeting (25%)
Use `get_linkedin_ads_demographics` segments to evaluate:
- L07 Job title targeting uses **specific titles**, not just functions —
  check `job_function` pivot; if the top 3 functions represent > 70% of
  impressions without job-title filters layered on, flag WARN (High)
- L08 Company size filtering matches stated ICP — check `company_size` pivot (Medium)
- L09 Seniority level appropriate for offer — check `seniority` pivot (High)
- L10 Matched Audiences active — retargeting pools + uploaded contact lists (High)
- L11 ABM company lists uploaded (up to 300 000 companies supported) (Medium)
- L12 Audience expansion OFF for precision, ON for scale (intentional, not default) (Medium)
- L13 Predictive Audiences tested (replaced Lookalikes Feb 2024) (Medium)
- L14 Audience Network **OFF** unless isolated test budget (Medium)

### Creative Quality (20%)
Use `get_linkedin_ads_creative_performance`:
- L15 Thought Leader Ads active, **≥ 30% of LinkedIn budget for B2B** (High)
- L16 Ad format diversity — ≥ 2 formats tested (single image, carousel, video, document) (High)
- L17 Video ads tested (Medium)
- L18 Creative refresh every 4–6 weeks — flag any creative active > 6 weeks
  with declining engagement_rate (Medium)
- L19 Document Ads considered — benchmark 7% engagement rate (Low)

### Lead Gen & Performance (15%)
Use `get_linkedin_ads_lead_gen_performance`:
- L20 Lead Gen Form ≤ 5 fields — target 13% CVR; if form_completion_rate <
  10% flag WARN (High)
- L21 Lead Gen Form synced to CRM in real-time (High)
- L22 Campaign objective matches funnel stage (High)
- L23 Lead-to-opportunity rate tracked — compare LinkedIn leads to HubSpot
  deals with `utm_source=linkedin`; CPL alone is insufficient (High)
- L24 Attribution window configured: 30-day click / 7-day view (Medium)
- L25 Demographics report reviewed monthly (operational) (Low)

### Bidding & Budget (15%)
- L26 Bid strategy: Manual CPC for early-stage; Maximum Delivery only at
  scale with data (High)
- L27 Daily budget ≥ €40 for Sponsored Content (High)
- L28 CTR (Sponsored Content) ≥ 0.44% (High)
- L29 Average CPC within €5.50–€9.00 (B2B Spain) (Medium)
- L30 TLA CPC within €2–€3.80 (Medium)
- L31 No Sponsored Messaging / InMail / Conversation Ads in use
  (EU-discontinued Jan 2022) — **fail immediately if present** (Critical)

## Thought Leader Ads (TLA) — Always Check

TLA (employee / executive personal posts sponsored) now accepts non-employee
members since March 2025. Typically 2–5× engagement of standard SC and ~3×
cheaper CPC. If TLA share < 30% of budget for a B2B client, raise a **High**
priority recommendation.

## ABM Strategy (B2B Enterprise clients only)

- Company list uploaded, segmented by tier (Tier 1/2/3)
- Custom content per tier (personalised messaging)
- Account penetration tracking (contacts reached per target account)
- Integration with CRM / ABM platform (Demandbase, 6sense, HubSpot ABM)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-linkedin-audit/LINKEDIN-ADS-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: linkedin_ads PERIOD: <start>..<end>
```

Sections:
1. Score breakdown per category
2. **TLA adoption roadmap** if TLA budget share < 30%
3. **ABM strategy recommendations** for B2B Enterprise
4. **Lead Gen Form optimization priorities** — flag each form with
   completion_rate < 10% or cost_per_lead > target
5. All findings grouped by category with check IDs
6. Quick Wins

## Non-Negotiables

- Use new LinkedIn terminology (Oct 2025 rename)
- Never recommend Sponsored Messaging for Spain
- Every threshold cites `benchmarks-spain.md`
- Compliance language cites `compliance-eu-spain.md`
