---
name: ads-strategy-plan
description: >
  Strategic paid-advertising plan for a Spanish client: platform selection,
  campaign architecture, budget planning, creative strategy, tracking setup,
  and a phased rollout roadmap. Interactive — suitable for kickoff, not for
  cron automation. Activate when user says "ad plan", "ad strategy", "media
  plan", "new client kickoff", "PPC strategy", or "campaign plan".
---

# Strategic Paid Advertising Plan — Spain

This skill is **human-in-the-loop** (interactive by design) and stays out of
the automated `ads-audit` bundle. Use it for kickoffs and strategy refreshes.

All numbers reference `.claude/references/benchmarks-spain.md`; all regulatory
language references `.claude/references/compliance-eu-spain.md`.

## Process

### 1. Discovery
Ask the user:
- Business type, offer, target audience (Spain / EU / LATAM?)
- Current advertising status (`list_clients` + `get_cross_channel_summary` if
  the client already exists in the MCP)
- Goals: awareness / lead gen / e-commerce sales / app installs
- Monthly budget range in EUR
- In-house creative capacity vs outsourced

### 2. Competitive analysis (lightweight)
- Identify 3–5 competitors (user-provided)
- Check presence on Meta Ad Library, Google Ads Transparency, LinkedIn Ad
  Library (DSA Ad Repositories — user opens in browser, not scraped)
- Note messaging themes, creative approaches, keyword / audience gaps

### 3. Platform selection
Use the Platform Selection Matrix from `ads-budget-review` (same matrix;
Spanish-client calibrated). Load matching industry pattern:
- SaaS B2B
- E-commerce (retail / wellness / DTC)
- Local service (reformas, clínicas, legal, asesorías)
- B2B Enterprise
- Automotive (ties into Walcu clients)
- Wellness / Salud (avoid Rx-drug-to-consumer — illegal in Spain per Ley 29/2006)

### 4. Campaign architecture

Naming convention:
```
[Platform]_[Objective]_[Audience]_[Geo]_[Date]
```
Example: `META_CONV_Prospecting_ES_2026Q2`

Template:
```
Account
├── Brand Campaign (always-on)
├── Non-Brand Prospecting
│   ├── Top Funnel — Awareness
│   ├── Mid Funnel — Consideration
│   └── Bottom Funnel — Conversion
├── Retargeting
│   ├── Website visitors (7–30 days)
│   ├── Engaged users (video views, social engagement)
│   └── Cart abandoners / form starters
└── Testing
    └── New audiences / formats / messaging
```

### 5. Budget planning
Apply 70/20/10:
- 70% proven — primary platforms with proven ROI
- 20% scaling — platforms showing promise
- 10% testing — new strategies

Pacing:
- Month 1–2: heavy testing, elevated CPA (learning)
- Month 3–4: optimise, tighten targeting
- Month 5–6: scale winners, kill losers
- Ongoing: 70/20/10 with quarterly reviews

### 6. Creative strategy
5 content pillars:
- Pain point
- Social proof
- Product demo
- Offer
- Education

Production plan priority:
1. Product / service videos 15–30 s (Meta, YouTube)
2. Static images (Google display / Meta / LinkedIn)
3. Carousel / collection (Meta, LinkedIn)
4. UGC / testimonial video (Meta)
5. Long-form video 1–3 min (YouTube)

### 7. Tracking setup

| Platform | Client-side | Server-side | Priority |
|---|---|---|---|
| Google | gtag.js | Enhanced Conversions + GTM SS | P1 |
| Meta | Pixel | CAPI | P1 |
| LinkedIn | Insight Tag | CAPI (2025) | P2 |
| GA4 | gtag.js | Measurement Protocol (optional) | P1 |

Consent stack requirements (see `compliance-eu-spain.md`):
- CMP integrated (Cookiebot / OneTrust / Didomi / Funnel / Iubenda)
- Consent Mode v2 advanced
- AEPD-compliant banner (reject-all equal prominence)
- GDPR DPAs signed with each platform

### 8. Implementation roadmap

- **Weeks 1–2 — Foundation:** install tracking, set up conversion events,
  create campaign structure, build audiences, produce first creative batch
- **Weeks 3–4 — Launch:** launch primary platform, conservative bidding,
  monitor daily, verify tracking
- **Weeks 5–8 — Optimise:** analyse ≥ 2 weeks of data, adjust bidding, kill
  under-performers (3× Kill Rule), launch secondary platform, start A/B tests
- **Weeks 9–12 — Scale:** apply 20% Rule to winners, expand to testing
  platforms, implement advanced strategies (Advantage+, Smart Bidding, ABM)

## Deliverables

Under `./reports/<client_id>/<YYYY-MM-DD>-strategy/`:
- `ADS-STRATEGY.md` — full plan
- `CAMPAIGN-ARCHITECTURE.md` — structure + naming
- `BUDGET-PLAN.md` — allocation with monthly pacing
- `CREATIVE-BRIEF.md` — production plan
- `TRACKING-SETUP.md` — implementation checklist + AEPD compliance checklist
- `IMPLEMENTATION-ROADMAP.md` — phased timeline

## KPI Targets (directional)

| Metric | Month 1 | Month 3 | Month 6 | Month 12 |
|---|---|---|---|---|
| ROAS | Baseline | Target −20% | Target | Target +20% |
| CPA | Baseline | Target +30% | Target | Target −10% |
| CVR | Baseline | +10% | +20% | +30% |
| CTR | Baseline | +15% | +25% | +30% |
| Budget | Testing | Optimizing | Scaling | Maintaining |

## Non-Negotiables

- Use EUR and Spain benchmarks exclusively
- Never recommend LinkedIn Sponsored Messaging for EU targeting
- Never recommend US-special-category ad flows — use EU equivalents
- Tracking must include CMP + Consent Mode v2 advanced — flag as P1 if absent
- This skill is interactive — it is NOT invoked by `ads-audit`
