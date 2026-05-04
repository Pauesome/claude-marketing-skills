---
name: landing-page-audit
description: >
  Landing page quality audit for paid ad campaigns (Spain). Evaluates message
  match, page speed (LCP / INP / CLS), mobile experience, trust signals, form
  optimization, AEPD cookie banner compliance, and conversion tracking.
  Correlates landing page performance with GA4 and ad-channel data. Activate
  when the user says "landing page audit", "post-click experience", "landing
  page quality", "conversion rate", or "message match".
---

# Landing Page Audit — Spain

All numerical thresholds come from `.claude/references/benchmarks-spain.md`
(Landing Page section). AEPD consent-banner rules come from
`.claude/references/compliance-eu-spain.md`.

## Required Inputs

- `client_id` — for ad-to-page correlation
- `urls` — list of landing page URLs to audit (if omitted, pull top landing
  pages from `get_ga_landing_page` ordered by paid-traffic sessions)
- `date_range_start` / `date_range_end` — default 30 days
- Fail fast if neither client_id nor explicit URLs given.

## Data Collection

**MCP tools:**
1. `get_ga_landing_page` — sessions, users, engagement, conversions per page
2. `get_ga_page_performance` — cross-reference engagement trends
3. `get_ga_channel_performance` — isolate Paid Search / Paid Social traffic to
   weight which pages matter most
4. `get_ga_device_performance` — confirm mobile share (drives mobile weight)

**Web inspection:**
5. For each URL, use `WebFetch` to pull HTML and extract:
   - H1, primary CTA, form fields, visible offer
   - Consent banner structure (AEPD compliance)
   - `<meta viewport>`, font sizes, image formats
   - Third-party scripts count
   - Note: we cannot measure real LCP / INP / CLS without a browser. Record
     them as "unmeasured — require PageSpeed Insights or Chrome DevTools" and
     flag if the user wants true speed data

## Score Components

```
Message Match   25%
Page Speed      25%   (Pass: LCP < 2.5s, INP < 200ms, CLS < 0.1)
Mobile UX       20%
Trust Signals   15%
Form Quality    15%
```

## Checks

### Message Match (LP-MM-01 … 05)
- LP-MM-01 Landing page H1 reflects ad copy headline / target keyword
- LP-MM-02 Promoted offer (price, discount, trial) visible above the fold
- LP-MM-03 Landing CTA matches ad's promised action
- LP-MM-04 Consistent imagery between ad creative and page
- LP-MM-05 Search keyword appears naturally in page content

Scoring: Exact (100), Partial (60), Weak (30), Mismatch (0).

### Page Speed (LP-SP-01 … 05)
Critical thresholds (all from `benchmarks-spain.md`):
- LP-SP-01 LCP < 2.5 s (source: PageSpeed Insights or Chrome DevTools)
- LP-SP-02 INP < 200 ms
- LP-SP-03 CLS < 0.1
- LP-SP-04 Page weight < 2 MB
- LP-SP-05 No render-blocking scripts above the fold

### Mobile UX (LP-MOB-01 … 07)
- LP-MOB-01 Tap targets ≥ 48 × 48 px with ≥ 8 px spacing
- LP-MOB-02 Body font ≥ 16 px (no pinch-to-zoom)
- LP-MOB-03 Input fields sized correctly; keyboard type matches
- LP-MOB-04 CTA full-width on mobile, above fold
- LP-MOB-05 No horizontal scroll
- LP-MOB-06 Phone numbers clickable (`tel:` link)
- LP-MOB-07 No popups / interstitials blocking content on load

### Trust Signals (LP-TR-01 … 05)
- LP-TR-01 Company logo above fold
- LP-TR-02 Social proof (reviews, customer count, rating) above fold
- LP-TR-03 Security / guarantee badges near CTA
- LP-TR-04 Below-fold: full testimonials with name, photo, company
- LP-TR-05 Privacy policy, physical address (local service), registration
  numbers where legally required (e.g., registro sanitario, colegiado)

### Form Quality (LP-FM-01 … 07)
- LP-FM-01 Form length appropriate for funnel stage:
  - Top-funnel: 1–3 fields (Pass), 4–5 (Warn), 6+ (Fail)
- LP-FM-02 Multi-step form for 5+ fields
- LP-FM-03 Inline validation (no submit-then-error)
- LP-FM-04 Submit CTA specific ("Pide tu presupuesto gratis", not "Enviar")
- LP-FM-05 Pre-fill known fields (UTM, session data)
- LP-FM-06 Progress indicator on multi-step forms
- LP-FM-07 Thank-you page has clear next steps + fires conversion event

### Consent / AEPD (LP-CO-01 … 06) — CRITICAL
Per AEPD Nov 2023 guide (see `compliance-eu-spain.md`):
- LP-CO-01 Reject-all button present with same prominence as accept-all
  (size / colour / contrast / position)
- LP-CO-02 No pre-ticked boxes
- LP-CO-03 Banner does not cover primary CTA on load
- LP-CO-04 Banner does not push headline / offer below the fold
- LP-CO-05 Essential cookies allowed without consent; analytics / ads /
  personalization require explicit consent
- LP-CO-06 Consent Mode v2 advanced mode implemented (Google + Microsoft stack)

Each LP-CO failure is **Critical** severity (regulatory exposure).

### Tracking (LP-TK-01 … 04)
- LP-TK-01 Google tag / Meta Pixel / LinkedIn Insight Tag firing on thank-you page
- LP-TK-02 UTM parameters captured and stored
- LP-TK-03 Click IDs preserved (`gclid`, `fbclid`, `li_fat_id`)
- LP-TK-04 Click IDs passed to form submissions / CRM (HubSpot hidden fields)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-landing-audit/LANDING-PAGE-REPORT.md`.

First non-empty line:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> SCOPE: landing PERIOD: <start>..<end>
```

Sections per URL:
1. Score + grade
2. Message-match analysis (ad copy → LP content, per source campaign)
3. Speed findings (measured or "PageSpeed Insights required")
4. Mobile issues
5. Trust signal gaps
6. Form findings
7. **AEPD compliance** (prominent — any failure is Critical)
8. Tracking / UTM / click-ID handoff
9. Quick Wins

## Non-Negotiables

- AEPD cookie-banner failures are always Critical
- Never assume speed numbers you haven't measured — flag as "unmeasured"
- Weight mobile more heavily when GA4 says > 70% of sessions are mobile
- Reference `benchmarks-spain.md` for all thresholds
