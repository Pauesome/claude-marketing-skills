---
name: ads-audit
description: >
  Full multi-platform paid advertising audit for Spanish clients. Orchestrates
  parallel platform-specific audits (Google, Meta, LinkedIn) plus cross-cutting
  creative, tracking, budget, and compliance (GDPR/LOPDGDD/AEPD) subagents.
  Produces a unified Ads Health Score and action plan. Activate when the user
  says "audit", "full ad check", "analyze my ads", "account health", or "PPC audit".
---

# Full Multi-Platform Ads Audit — Spain

You are the orchestrator for a multi-platform paid-advertising audit. Your job
is to spawn subagents in parallel, collect their scored findings, and produce
a unified report. Every number you cite must reference
`.claude/references/benchmarks-spain.md`. Every compliance statement must
reference `.claude/references/compliance-eu-spain.md`.

## Required Inputs (must be explicit, no mid-run prompts)

- `client_id` — resolve via the `list_clients` MCP tool
- `date_range_start` / `date_range_end` — default to the last 30 days
- Optional `platforms` subset (default: all platforms the client has configured)

If any required input is missing, fail fast with an explicit error — **do not
prompt the user mid-audit**. This skill must be runnable non-interactively
(headless-friendly for future cron automation).

## Process

1. **Resolve client and active platforms**
   - Call `list_clients` to confirm the client exists
   - Check which platforms the client has configured (google_ads, meta_ads,
     linkedin_ads, ga, gsc, gtm, hubspot)
1a. **Load client brief** (if available)
   - Read `clients/briefs/<client_id>.md`
   - If the file exists, extract: business type, sector, product/service description,
     value proposition, and any compliance notes (e.g. financial services, healthcare)
   - If the file is missing, proceed with generic benchmarks and note the gap
   - **Pass the full brief text in the prompt context of every subagent Task call**
     so platform-specific scoring reflects the client's sector and goals
2. **Pull cross-channel context** — `get_cross_channel_summary` for the period
   to learn budget share per platform (drives aggregate weighting)
3. **Spawn subagents in parallel** using the Task tool (one `Task` call per
   subagent, all in a single message):
   - `audit-google` — if `client.google_ads` present
   - `audit-meta` — if `client.meta_ads` present
   - `audit-linkedin` — if `client.linkedin_ads` present
   - `audit-creative` — always (cross-platform creative synthesis)
   - `audit-tracking` — always (privacy + pixel + CAPI stack)
   - `audit-budget` — always (70/20/10 allocation)
   - `audit-compliance` — always (GDPR / LOPDGDD / AEPD / DSA)
4. **Validate**: every subagent must return a numeric score, category breakdown,
   and list of findings. If any subagent fails, note which and continue.
5. **Aggregate**
   ```
   Aggregate = Σ (platform_score × platform_budget_share)
   ```
   Cross-cutting scores (creative, tracking, budget, compliance) modify the
   aggregate by applying their grade as a multiplier (A = 1.0, B = 0.95,
   C = 0.85, D = 0.70, F = 0.50) — a failing compliance or tracking score
   caps the overall grade.
6. **Output**

## Output

Write three files under `./reports/<client_id>/<YYYY-MM-DD>-ads-audit/`:

- `ADS-AUDIT-REPORT.md` — comprehensive findings
- `ADS-ACTION-PLAN.md` — prioritised recommendations (Critical → High → Medium → Low)
- `ADS-QUICK-WINS.md` — items fixable in < 15 minutes with high impact

The **first non-empty line** of `ADS-AUDIT-REPORT.md` must be:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PERIOD: <start>..<end>
```

This header is parsed by the future scheduler to diff scores over time.

## Report Structure

### Executive Summary
- Aggregate Ads Health Score (0–100) + grade
- Per-platform scores
- Active platforms detected, business type inferred from GA4/HubSpot signals
- Top 5 critical issues across all platforms
- Top 5 quick wins

### Per-Platform Sections
Each section embeds the subagent's full output, preserving check IDs.

### Cross-Platform Analysis
- Budget allocation: actual vs recommended (70/20/10) given client's business type
- Tracking consistency: are the same conversion events fired to every platform?
- Creative consistency: messaging aligned across platforms?
- Attribution overlap: double counting risk between Google / Meta / GA4 / HubSpot

### Strategic Recommendations
- Platform prioritisation
- Budget reallocation recommendations
- Scale list (ready-to-scale campaigns) and Kill list (3× Kill Rule violations)

## Priority Definitions (reference in every finding)

- **Critical** — revenue / data / regulatory loss risk — fix immediately
- **High** — significant performance drag — fix within 7 days
- **Medium** — optimization opportunity — fix within 30 days
- **Low** — best practice, backlog

## Quick Wins Criteria

```
IF severity ∈ {Critical, High}
AND estimated_fix_time < 15 minutes
THEN flag as Quick Win
SORT BY (severity_multiplier × estimated_impact) DESC
```

## Non-Negotiables

- No hardcoded benchmarks in your output — read them from
  `.claude/references/benchmarks-spain.md`
- No US regulations — use `.claude/references/compliance-eu-spain.md`
- No interactive prompts — all parameters come up-front
- Every finding must cite its check ID and severity
- Weight ROAS and CPA above rate metrics (CTR / CVR) when scoring
