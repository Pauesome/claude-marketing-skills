---
name: ab-test-design
description: >
  A/B test design and experiment planning for paid ads in Spain. Structured
  hypothesis framework, sample-size calculator, duration estimator, and
  platform-specific setup (Meta Experiments, Google Experiments, LinkedIn
  A/B). Activate when user says "A/B test", "split test", "experiment design",
  "test hypothesis", "statistical significance", "sample size", or "test duration".
---

# A/B Test Design — Spain

Plans rigorous paid-ad experiments. Thresholds and sample-size lookup come from
`.claude/references/benchmarks-spain.md`.

## Required Inputs

Up-front (no mid-run prompts):
- Platform (google_ads / meta_ads / linkedin_ads)
- What is being tested (creative concept, hook, audience, bidding strategy,
  landing page, etc.)
- Baseline CVR (if not known, pull from MCP using client_id + 30-day window)
- Minimum Detectable Effect (MDE) — relative %
- Daily traffic or click volume per variant (pull from MCP if client_id given)

## Hypothesis Framework

Every test starts with a structured hypothesis. Enforce this format:

```
IF   we [change / action]
THEN [metric] will [increase / decrease] by [estimated %]
BECAUSE [reasoning based on prior data or insight]
```

Hypothesis quality checklist:
- [ ] Single variable isolated
- [ ] Specific metric defined (not "performance")
- [ ] Effect size stated (required for sample size)
- [ ] Timeframe defined
- [ ] Success / failure criteria fixed *before* launch

## Sample Size

```
n_per_variant = (Z_α + Z_β)² × 2 × p × (1 - p) / MDE²
Z_α = 1.96 (95% confidence)
Z_β = 0.84 (80% power)
p   = baseline conversion rate
MDE = relative detectable effect
```

For quick estimates, use the lookup table in `benchmarks-spain.md`
(Testing & Statistical Significance section).

## Duration

```
duration_days = n_per_variant / daily_traffic_per_variant
```
- Minimum 7 days (capture weekly patterns)
- Maximum 28 days (avoid seasonal drift)
- Respect platform learning-phase floors: Google 7–14 d, Meta 3–7 d,
  LinkedIn 7–14 d

If the calculated duration < 7 days, still run ≥ 7 days.
If > 28 days, either increase MDE, increase traffic, or skip the test.

## Platform Setup

### Meta Experiments
- Ads Manager → Experiments (not manual duplication)
- Automatic audience splitting
- Budget: ≥ €75/day per variant
- Duration 7–14 d; Meta auto-declares winner at 95% confidence

### Google Experiments
- Campaign experiments or Ad Variations
- 50/50 traffic split
- Primary metric fixed before launch (conversions / CPA / ROAS)
- Duration 14–30 d; minimum 2 weeks for bidding tests

### LinkedIn A/B
- Built into Campaign Manager for Sponsored Content
- ≥ €40/day per variant
- Smaller daily volume → expect 14–21 d

## What to Test (Priority Order)

High impact (test first):
1. Creative concept (messaging angles, not colour swaps)
2. Hook (first 1–3 s of video)
3. Offer structure (pricing, discount, trial length)
4. Landing page (headline, CTA, form length)
5. Bidding strategy

Medium:
6. Audience targeting (interest vs Lookalike vs broad)
7. Ad format (static vs video vs carousel)
8. CTA button
9. Campaign structure (CBO vs ABO)

Low (test last):
10. Scheduling
11. Device targeting
12. Minor copy variations

## Common Mistakes to Avoid

- Multi-variable tests without factorial design
- Stopping early (before 95% confidence)
- Testing during holidays / launches
- Unequal time periods
- No documentation of prior learnings
- Testing tiny changes when a bigger intervention is needed

## Output Format

```
## A/B Test Plan

### Hypothesis
IF [change] THEN [metric] will [direction] by [amount] BECAUSE [reasoning]

### Design
| Parameter | Value |
|---|---|
| Platform | ... |
| Test type | A/B |
| Variable | ... |
| Control | ... |
| Variant | ... |
| Primary metric | ... |
| Traffic split | 50/50 |

### Sample Size & Duration
| Metric | Value |
|---|---|
| Baseline CVR | X% |
| MDE | X% |
| Required sample / variant | N |
| Daily traffic / variant | N |
| Estimated duration | X days |
| Minimum duration | 7 days |

### Success Criteria
- Winner declared at 95% confidence
- Primary metric improvement ≥ MDE sustained ≥ 7 days
- No regression on [secondary metric]

### Platform setup
<step-by-step for chosen platform>
```

## Non-Negotiables

- Never declare a winner without 95% confidence
- Never run < 7 days
- Never test two variables without factorial design
- Always reference Spain sample-size table in `benchmarks-spain.md`
