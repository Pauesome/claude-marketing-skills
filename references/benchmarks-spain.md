# Paid Ads Benchmarks — Spain (EUR)

All figures below are **guidance ranges, not hard cutoffs**. A campaign below a
target on one metric but with healthy **ROAS or CPA** is not a failing campaign —
score it as WARN, not FAIL, and always weight ROAS and CPA above raw rate
metrics (CTR, CVR, CPC). Good campaigns routinely sit below the averages here.

All currency is **EUR**. IVA (21%) is **excluded** from ad spend; include IVA
only when computing gross-margin-based metrics (Break-Even CPA, LTV:CAC).
Flag unit-economics calculations that mix with-IVA revenue and without-IVA
spend — that produces misleading margins.

---

## Scoring Scale (applies to every audit skill)

| Grade | Score | Meaning |
|---|---|---|
| A | 90–100 | Minor optimizations only |
| B | 75–89 | Some improvement opportunities |
| C | 60–74 | Notable issues need attention |
| D | 40–59 | Significant problems present |
| F | <40 | Urgent intervention required |

Severity multipliers for individual checks:
- **Critical** (×5.0) — revenue/data loss risk, fix immediately
- **High** (×3.0) — significant performance drag, fix within 7 days
- **Medium** (×1.5) — optimization opportunity, fix within 30 days
- **Low** (×1.0) — best practice, minor impact

Pass = full credit. Warning = 50% credit. Fail = 0% credit.

---

## Google Ads (Spain)

### Rate & Cost Benchmarks

| Metric | Pass | Warning | Fail | Notes |
|---|---|---|---|---|
| Avg CPC (Search) | ≤ €1.00 | €1.00–€2.00 | > €2.00 | High-competition verticals (legal, finance, insurance, health, real estate) expect up to €2.00 avg; everything else should sit near €1 |
| CTR (Search) | ≥ 5.5% | 3.0%–5.5% | < 3.0% | |
| CVR (Search) | ≥ 3% retail / ≥ 1% B2B SaaS | half to target | well below target | Guidance only — weight ROAS/CPA above CVR |
| Quality Score (weighted avg) | ≥ 7 | 5–6 | ≤ 4 | |
| Wasted spend (0-conv terms >€10) | < 5% | 5–15% | > 15% | |
| Invalid clicks | < 5% | 5–10% | > 10% | |
| RSA Ad Strength | Good / Excellent | Average | Poor | |
| Search impression share (branded) | ≥ 80% | 60–80% | < 60% | |
| Budget-lost IS | < 10% | 10–20% | > 20% | >20% = add budget |
| Rank-lost IS | < 20% | 20–35% | > 35% | >35% = bid / QS work |

### Budget Minimums (EUR/day)

| Campaign type | Minimum | Learning phase target |
|---|---|---|
| Search | €15/day | ≥ 15 conversions / month |
| Performance Max | €40/day | Sufficient for algorithmic optimization |
| Shopping (standard) | €20/day | ≥ 15 conversions / month |
| Demand Gen | €30/day | — |
| YouTube (video views) | €20/day | — |

---

## Meta Ads (Spain)

### Rate & Quality Benchmarks

| Metric | Pass | Warning | Fail | Notes |
|---|---|---|---|---|
| EMQ (Purchase event) | ≥ 8.0 | 6.0–7.9 | < 6.0 | Lower CVR clients still need EMQ ≥ 6 |
| Event dedup rate | ≥ 90% | 70–90% | < 70% | |
| CTR | ≥ 1.0% | 0.5–1.0% | < 0.5% | Retail often below Spain B2B |
| Creative formats active | ≥ 3 | 2 | 1 | Image, video, carousel, collection |
| Creatives per ad set | ≥ 5 | 3–4 | < 3 | |
| Prospecting frequency (7d) | < 3.0 | 3.0–5.0 | > 5.0 | |
| Retargeting frequency (7d) | < 8.0 | 8.0–12.0 | > 12.0 | |
| Learning Limited ad sets | < 30% | 30–50% | > 50% | |
| Budget per ad set | ≥ 5× target CPA | 2×–5× | < 2× | |
| Andromeda distinct creatives | ≥ 10 | 5–9 | < 5 | Genuinely distinct concepts, not variations |

### Budget Minimums (EUR/day)

| Scope | Minimum | Note |
|---|---|---|
| Ad set (manual) | €15/day | ≥ 5× target CPA recommended |
| Advantage+ Sales campaign | €75/day | Lower starves learning |
| Learning-phase minimum spend | ≥ 5× CPA × 7 days | Sustained |

---

## LinkedIn Ads (Spain / EU)

### Rate & Cost Benchmarks

| Metric | Pass | Warning | Fail | Notes |
|---|---|---|---|---|
| CTR (Sponsored Content) | ≥ 0.44% | 0.30–0.44% | < 0.30% | |
| Avg CPC (Sponsored Content) | €5.50–€9.00 | €9–€12 | > €12 | B2B Spain; senior targeting trends higher |
| TLA CPC | €2.00–€3.80 | €3.80–€5.00 | > €5.00 | Thought Leader Ads are ~3× cheaper |
| Lead Gen Form CVR | ≥ 10% | 5–10% | < 5% | ≤5 fields target 13% |
| Message frequency | ≤ 1 / 30d | 1 / 15–30d | > 1 / 15d | Do not use for EU targeting — Sponsored Messaging discontinued in EU since Jan 2022 |
| TLA budget share (B2B) | ≥ 30% | 15–30% | < 15% | |

### Budget Minimums (EUR/day)

| Scope | Minimum | Note |
|---|---|---|
| Sponsored Content campaign | €40/day | Below this = broken learning, not a real test |
| Lead Gen campaign | €40/day | Same |
| ABM list-based | €50/day | Narrower audience, needs headroom |

### Audience Size
- Minimum to run: **500 members**
- Below 2,000 = very narrow, expect volatile delivery

---

## Cross-Channel / Business Unit Economics

These ratios are **margin-driven, not region-driven** — keep universal:

| Metric | Pass | Warning | Fail |
|---|---|---|---|
| LTV : CAC | ≥ 3 : 1 | 1 : 1 – 2 : 1 | < 1 : 1 |
| MER (e-commerce) | 3×–8× | 2×–3× | < 2× |
| MER (SaaS) | 5×–10× | 3×–5× | < 3× |
| MER (local service) | 3×–8× | 2×–3× | < 2× |
| CAC payback (SaaS) | ≤ 12 months | 12–18 | > 18 |

### Break-Even Formulas (Spain)

```
Break-Even CPA  = AOV × Gross Margin %         (both pre-IVA)
Break-Even ROAS = 1 / Gross Margin %
```

Always compute margin on **pre-IVA** revenue and **pre-IVA** spend. If the
client reports revenue with IVA included, divide by 1.21 before using it here.

---

## Kill / Scale Rules

| Rule | Threshold | Data required | Action |
|---|---|---|---|
| 3× Kill | CPA > 3 × target | ≥ 7 days, ≥ 20 clicks | Pause |
| No-conv kill | 0 conversions | ≥ €80 spend or ≥ 50 clicks | Pause and diagnose |
| Creative kill | CTR < 50% of platform benchmark | ≥ 1 000 impressions | Kill creative |
| ROAS kill | ROAS < 50% of target | ≥ 14 days | Cut budget 50% or pause |
| 20% Scale | Budget increase | Any scale event | Cap at +20% per change; wait 3–5 days before next |
| Ready to scale | CPA under target 2+ weeks AND ≥ 50 conv/week AND no fatigue | — | Scale +20% |

---

## Landing Page (Spain traffic)

75%+ of Spanish mobile ad clicks; mobile experience dominates.

| Metric | Pass | Warning | Fail |
|---|---|---|---|
| LCP | < 2.5s | 2.5–4.0s | > 4.0s |
| INP | < 200ms | 200–500ms | > 500ms |
| CLS | < 0.1 | 0.1–0.25 | > 0.25 |
| Page weight | < 2 MB | 2–5 MB | > 5 MB |
| Tap target | ≥ 48×48 px | — | < 48×48 px |
| Body font | ≥ 16 px | — | < 16 px |
| Form fields (top-funnel) | 1–3 | 4–5 | 6+ |
| Message match | Exact (100%) | Partial (60%) | Weak or mismatch (< 30%) |

Consent banner rules (AEPD Nov 2023): reject-all button must match accept-all
visual prominence; no pre-ticked boxes; banner must not cover primary CTA on
load. Violations score FAIL regardless of speed.

---

## Testing & Statistical Significance

Sample size per variant (95% confidence, 80% power):

| Baseline CVR | 5% MDE | 10% MDE | 20% MDE | 30% MDE |
|---|---|---|---|---|
| 1% | 612 000 | 153 000 | 38 300 | 17 000 |
| 2% | 302 400 | 75 600 | 18 900 | 8 400 |
| 5% | 116 800 | 29 200 | 7 300 | 3 200 |
| 10% | 55 200 | 13 800 | 3 450 | 1 530 |

Duration: minimum 7 days (weekly patterns). Maximum 28 days (seasonal drift).
Learning phase floor: Google 7–14 d, Meta 3–7 d, LinkedIn 7–14 d.

---

## Quick Wins (applied to any audit output)

An audit finding is a **Quick Win** when:
- Severity = Critical or High
- Estimated fix time < 15 minutes
- Sort by `severity_multiplier × estimated_impact` DESC
