---
name: ppc-math
description: >
  PPC financial calculator for Spanish clients. CPA, ROAS, CPL, break-even,
  impression-share opportunity, budget forecast, LTV:CAC, MER. Can pull live
  data from the MCP (ad performance + HubSpot revenue + GA4) or work from
  pasted numbers. Handles EUR and IVA correctly. Activate when the user says
  "PPC math", "break-even", "ROAS calculator", "CPA calculator", "budget
  forecast", "LTV CAC", "MER", or asks for any ad financial modeling.
---

# PPC Math & Financial Modeling — Spain

Pure calculation skill. Benchmarks and unit-economics guidance come from
`.claude/references/benchmarks-spain.md`.

## IVA Handling (Spain-specific, non-optional)

Ad platforms bill spend **without IVA** (reverse charge). Client revenue is
usually reported **with IVA (21%)**. Mixing the two inflates margins.

Default rule: always work in **pre-IVA** values. If the user gives revenue
figures from a CRM / accounting system, ask whether they include IVA — if yes,
divide by 1.21 before using them in margin / LTV calculations.

The `ads-budget-review` skill reuses this convention.

## Live-Data Mode (MCP)

When the user supplies a `client_id`, you can pull inputs directly:
- Ad spend: `get_cross_channel_summary` + `get_google_ads_campaign_performance`
  + `get_meta_campaign_performance` + `get_linkedin_ads_campaign_performance`
- Revenue / deals: `get_hubspot_deals` (filter by `utm_source` for per-platform ROAS)
- Conversions: `get_ga_conversion_performance`

Always print the exact inputs you pulled so the calculation is auditable.

## Paste-Data Mode

If the user pastes numbers without a client_id, accept them directly.

## Calculators

### 1. CPA
```
CPA = Spend / Conversions
```
Compare against the client's internal target CPA; flag if > 3× target
(3× Kill Rule).

### 2. ROAS
```
ROAS = Revenue / Spend
ROAS% = (Revenue - Spend) / Spend × 100
```
Break-even ROAS = 1 / gross margin. Flag if ROAS < break-even.

### 3. Break-Even
```
Break-Even CPA  = AOV × Gross Margin %
Break-Even ROAS = 1 / Gross Margin %
```
Both numbers are pre-IVA. State the margin assumption.

### 4. Impression Share Opportunity (Google only)
```
Revenue opportunity = Current Revenue × (1 / Current IS - 1)
```
Decompose IS lost into budget vs rank:
- Budget-lost IS > 20% → recommend +20% budget
- Rank-lost IS > 35% → recommend Quality Score or bid work
Source: `get_google_ads_impression_share`.

### 5. Budget Forecast
```
Projected Spend       = Daily Budget × Days
Projected Conversions = Projected Spend / Historical CPA
Projected Revenue     = Projected Conversions × AOV
```
Three scenarios: +20% (conservative), +50% (moderate), +100% (aggressive —
warn about diminishing returns and 20% Scaling Rule).

### 6. LTV : CAC
```
CAC      = Total Marketing Spend / New Customers
LTV      = ARPU × Avg Customer Lifespan        (pre-IVA)
LTV:CAC  = LTV / CAC
```
Interpretation:
- < 1 : 1 — losing money per customer
- 1 : 1 – 2 : 1 — break-even to marginal
- ≥ 3 : 1 — healthy
- ≥ 5 : 1 — may be under-investing in growth

Payback period = CAC / (ARPU × Gross Margin).

### 7. MER
```
MER = Total Revenue / Total Marketing Spend
```
Benchmarks (from `benchmarks-spain.md`):
- E-commerce: 3–8×
- SaaS: 5–10×
- Local service: 3–8×

## Output Format

Every calculation output follows this template:

```
## PPC Financial Analysis — <Calculator Name>

**Inputs** (pre-IVA):
- …

**Calculation:**
  <formula>
  = <worked values>
  = <result>

**Result:**
| Metric | Value | Benchmark | Status |
|---|---|---|---|
| … | … | … | PASS/WARN/FAIL |

**Interpretation:**
<1–2 sentences>

**Recommendation:**
<one actionable next step>
```

## Non-Negotiables

- Always state whether inputs are pre- or post-IVA; never mix
- Round to 2 decimals for currency, 2 decimals for ratios
- Flag any calculation that compares a benchmark from another market — this
  skill only uses Spain values
- Never invent inputs; ask the user or pull from MCP
