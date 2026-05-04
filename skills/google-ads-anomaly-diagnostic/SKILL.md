---
name: google-ads-anomaly-diagnostic
description: >
  Diagnose a sudden Google Ads performance change — CPA spike, conversion
  drop, CTR collapse, impression loss, spend surge, or ROAS decline. Produces
  a root-cause analysis, not a full audit. Compares period-over-period,
  segments by campaign / device / geo / query, and distinguishes real
  performance problems from tracking gaps, seasonality, and statistical
  noise. Activate when the user says "CPA spiked", "conversions dropped",
  "performance issue", "why did [metric] change", "diagnose account",
  "account went wrong", or reports a specific anomaly.
---

# Google Ads Anomaly Diagnostic — Spain

Root-cause analysis for a specific performance change. Different workflow
from `google-ads-deep-audit` — this skill **starts from a known problem**
and asks "what explains it?", while the audit asks "is anything wrong?".

## Required Inputs

- `client_id` (required)
- `metric` (required) — one of `cpa`, `cpl`, `roas`, `cvr`, `ctr`,
  `impressions`, `spend`, `conversions`, `clicks`
- `direction` (required) — `up` or `down`
- `anomaly_window_start` / `anomaly_window_end` — the window where the
  anomaly was observed (default: last 7 days)
- `baseline_window_start` / `baseline_window_end` — what to compare
  against (default: prior 28 days ending the day before anomaly window)

Fail fast on missing inputs. Never guess the metric or direction —
without them the diagnosis is generic.

## Client Brief

Read `clients/briefs/<client_id>.md` for:

- Sector seasonality (LeadGenCo spikes in Jan/Sep around tax / retirement
  planning; Ferrer-Ponseti spikes pre-Christmas and mid-summer; LeadGenCo
  slumps in August)
- Known event calendar: product launches, landing page changes,
  holidays (Semana Santa, August holiday, Black Friday)
- Primary KPI — so the report leads with the metric that matters most
  to the client, even if the user asked about a secondary one

If the user reported a CPL spike but the brief says the client tracks
won revenue via offline conversion import, expand the scope to check
whether the offline import is lagging (a common false-positive for
"CPA spike").

## Data Collection (MCP Tools, parallel)

Both windows fetched side-by-side for every call.

1. `get_google_ads_campaign_performance` — campaign × day for both
   windows. Foundation for segmenting the anomaly to specific campaigns.
2. `get_google_ads_search_terms` — both windows. New query patterns
   (especially junk / irrelevant terms) often explain spend surges.
3. `get_google_ads_keywords` — both windows with `min_impressions: 50`.
   Look for keywords that lost impression share or gained volume
   suspiciously.
4. `get_google_ads_impression_share` — both windows. Budget-lost vs
   rank-lost IS swings are strong causal signals.
5. `get_ga_conversion_performance` (if GA4 configured) — both windows.
   GA4 vs Google Ads divergence → likely tracking issue, not performance.

## Diagnosis Hierarchy

Work through these layers in order. Stop when a clear root cause is
identified — do not over-diagnose.

### Layer 1 — Tracking gap (false positive)

Before concluding a real performance drop, rule these out:

- **Conversion lag**: for long-cycle clients (LeadGenCo ~120d, SaaSCo 30d+),
  conversions attributed to recent clicks are still trickling in. A "drop"
  in the last 7 days may just be incomplete data.
- **GA4 vs Google Ads divergence**: if GA4 shows stable conversions
  but Google Ads shows a drop, the tracking is broken (Consent Mode v2
  misconfig, gtag missed deploy, Enhanced Conversions field mismatch).
- **Offline conversion import lag**: if the client imports CRM
  conversions, an import lag shows as a CPA spike that self-corrects.
- **Attribution model change**: Google forced data-driven rollout may
  have reattributed historical conversions.

If any of these fire, report as **Tracking Issue (Not a Performance
Issue)** and exit the diagnosis. Recommend the tracking fix — not bid
changes.

### Layer 2 — External / account-level causes

- **Budget change**: did daily budget or campaign budget change in
  baseline → anomaly window?
- **Bid strategy change**: tCPA target moved, or strategy switched from
  Manual CPC → MaxConv (common rookie move that spikes spend)
- **New campaign launched**: eating impression share / budget from
  existing campaigns
- **Seasonality**: check brief's event calendar
- **Policy / disapproval**: if impressions collapsed on a specific
  campaign, check for ad disapprovals (flag for manual review — the
  MCP can't see this directly)
- **Landing page / website outage or change**: correlate with conversion
  drop (ask the user)

### Layer 3 — Query-level shift (what users searched)

Compare search terms between windows:

- **New wasted-spend queries**: surge in irrelevant terms (jobs,
  informational, competitor brand variants) → broad match expanded,
  negatives missing
- **Lost high-converting queries**: previous high performers dropped
  off → negatives too aggressive, budget limits, or competitive
  pressure
- **CTR shift on existing queries**: same queries, lower CTR → ad
  copy fatigue or new competitor with better copy

### Layer 4 — Creative / QS degradation

- RSA Ad Strength dropped (if available)
- Quality Score distribution shifted — more QS < 5 keywords → ad
  relevance or LPE dropped
- If QS moved but copy didn't change, investigate landing page
  (page speed regression, content change)

### Layer 5 — Auction competition

- Impression share: rank-lost IS increased → new competitor outbidding
- CPC increased without corresponding CTR/CVR improvement → auction
  heated up

## Scoring

This skill doesn't emit a health score — it produces a **confidence-rated
root cause**. The output ranks hypotheses by likelihood:

- **HIGH confidence** (one clear causal signal, others ruled out)
- **MEDIUM confidence** (two competing explanations)
- **LOW confidence** (noisy data, multiple small contributors)

If confidence is LOW, recommend a specific next check the user can run
(e.g. "pull last 14 days of change history" — not currently in MCP).

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-anomaly/`:

- `ANOMALY-DIAGNOSIS.md` — primary report
- `ANOMALY-CAMPAIGN-BREAKDOWN.md` — per-campaign delta table
- `ANOMALY-SEARCH-TERM-DIFF.md` — new vs lost queries between windows

First non-empty line of `ANOMALY-DIAGNOSIS.md`:

```
DIAGNOSIS: <root_cause_slug> CONFIDENCE: <HIGH|MEDIUM|LOW> CLIENT: <client_id> METRIC: <metric> DIRECTION: <up|down> BASELINE: <start>..<end> ANOMALY: <start>..<end>
```

### Report Structure

1. **TL;DR** — one-paragraph root cause + confidence
2. **Before / After Numbers** — the specific metric change in EUR and %
3. **Hypotheses Ranked** — top 3 explanations with evidence + ruled-out
   alternatives
4. **Recommended Action** — exactly what to do, in what order,
   within what timeframe. One recommendation per hypothesis.
5. **Monitoring** — what to watch over the next 7 / 14 / 28 days to
   confirm the fix worked

## Hard Rules

- **Always check Layer 1 (tracking) before Layer 2+** — a tracking
  misattribution looks identical to a real performance drop, and the
  wrong fix (cutting budget on a tracking-induced CPA spike) actively
  hurts the account.
- **Never recommend budget or bid changes based on < 7 days of data**
  unless the anomaly is > 50% swing AND confidence is HIGH.
- **Conversion lag caveat is mandatory** for any diagnosis on a
  date range ending within the client's conversion lag window
  (LeadGenCo: 30d+ caveat; SaaSCo: 14d+ caveat).
- When confidence is LOW, do **not** recommend action — recommend more
  investigation.
- Never attribute an anomaly to "algorithm change" without evidence —
  that's the null hypothesis, not a diagnosis.
