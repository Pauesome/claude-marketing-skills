---
name: google-ads-negative-keyword-builder
description: >
  Mine Google Ads search term reports and produce a ready-to-apply themed
  negative keyword list (Exact and Phrase match types) with a wasted-spend
  recovery estimate. Covers the four canonical themes for Spain — Empleo,
  Informacional, Competencia, Gratis / DIY — plus sector-specific themes
  from the client brief. Activate when the user says "build negatives",
  "negative keyword list", "find wasted spend", "clean up search terms",
  "reduce CPA", or asks for a negatives recommendation after an audit.
---

# Google Ads Negative Keyword Builder — Spain

Converts noisy search term data into a structured, themed negative-list
proposal that can be pasted directly into Google Ads Editor. Complements
`google-ads-deep-audit` — the audit flags the wasted spend; this skill
produces the fix.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 60 days (need
  enough data to see recurring patterns)
- `min_spend_threshold` (optional) — minimum EUR spend per term to
  consider. Default `€10`. Lower values surface more candidates at the
  cost of noise.
- `scope` (optional) — `account` (default), or a `campaign_id` /
  `campaign_name_contains` to scope to a single campaign

Fail fast on missing `client_id`. Never run with zero filters on high-
volume accounts — the noise-to-signal ratio is too low.

## Client Brief

Read `clients/briefs/<client_id>.md`. Critical context:

- **Product / service name** — to distinguish legitimate converting
  queries from lookalikes (LeadGenCo: "leadgenco bebé" or "leadgencolliw" are
  ambiguous; "leadgenco nuda propiedad" is product; "leadgenco offers jobs"
  is Empleo theme)
- **Competitor names** — for the Competencia theme
- **Adjacent-but-wrong products** — e.g. LeadGenCo should NOT match on
  "hipoteca inversa" queries (different product, different regulator);
  Ferrer-Ponseti audio should not match "ponseti clubfoot" (medical
  procedure, same surname)
- **Regulatory sensitivities** — financial-services clients must
  block "prestamos", "deuda", "morosos" themes unless the product
  actually covers those use cases

If brief is missing, refuse to run — false positives on sensitive
client queries can kill converting terms.

## Data Collection (MCP Tools)

1. `get_google_ads_search_terms` with:
   - `zero_conversions_only: false` — get ALL terms, filter later
   - `min_spend: 0` — no pre-filter; apply `min_spend_threshold` in-skill
   - `limit: 1000`
   - period from inputs
   - `campaign_ids` if scope is campaign-level

2. `get_google_ads_campaign_performance` — for the same period, to
   compute account-level CPA baseline (needed to tier severity)

3. `get_google_ads_keywords` — fetches current active keywords. Needed
   so proposed negatives do not block existing converting keywords.

## Classification Logic

For each search term, classify into one of these buckets. First match
wins (evaluated top-to-bottom).

| Bucket | Description | Default action |
|---|---|---|
| **Converting** | ≥ 1 conversion in the period | Skip — protect |
| **Empleo** | Contains "trabajo", "empleo", "curriculum", "CV", "vacantes", "sueldo", "carrera", "ofertas empleo", "gestiona tu curriculum" | Add as Phrase negative |
| **Informacional** | Contains "qué es", "como funciona", "significado", "definición", "ejemplo", "tutorial", "pdf", "wikipedia" | Add as Phrase negative unless brief identifies awareness-stage campaign |
| **Competencia** | Contains a competitor brand from the brief | Add as Exact or Phrase depending on brief instructions |
| **Gratis / DIY** | Contains "gratis", "gratuito", "free", "pirata", "torrent", "diy", "hazlo tú mismo" | Add as Phrase negative |
| **Ubicación errónea** | Contains a location outside the client's geo scope (e.g. "mexico", "argentina", "usa" for a Spain-only client) | Add as Exact for place names |
| **Wasted spend (no bucket match)** | Spend ≥ threshold, 0 conversions, doesn't fit above buckets | Add as Exact negative on the exact term |
| **Low-confidence ambiguous** | Shared stem with converting query OR matches a word also in current keyword list | Flag for human review — do NOT auto-add |

Sector-specific overrides from brief take precedence (e.g. a legal
client might WANT "gratis consulta" queries — don't block them).

## Match Type Rules

- **Empleo, Informacional, Gratis, Ubicación errónea** → Phrase match
  (`"trabajo"`) — these themes have many variants
- **Competencia** → follow brief (some clients want Exact to avoid
  blocking comparative queries; others want Phrase to block all
  competitor mentions)
- **Wasted-spend specific terms** → Exact (`[término]`) — don't over-block
- **Never** recommend Broad negatives (legacy BMM-style blocks too much)

## Level Placement

- **Shared negative list** (account level) for themes that apply across
  all campaigns: Empleo, Gratis, Ubicación errónea
- **Campaign level** for themes that may vary by campaign (Competencia
  on brand campaigns can be different from Competencia on non-brand)
- **Ad group level** for rare cannibalization fixes (only when two ad
  groups in the same campaign compete on a shared term)

## Scoring

This skill doesn't emit a full health SCORE. It emits a **recovery
estimate**:

```
RECOVERY: €<amount>/mo NEGATIVES: <count> CLIENT: <client_id> PERIOD: <start>..<end>
```

Where recovery = sum of spend on terms classified as wasted, with 0
conversions in the period, extrapolated to monthly.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-negatives/`:

- `NEGATIVES-REPORT.md` — executive summary with theme counts,
  recovery estimate, flagged-for-review list
- `NEGATIVES-SHARED-LIST.tsv` — Google Ads Editor import format
  (columns: Keyword, Match type, Shared list name)
- `NEGATIVES-CAMPAIGN-LEVEL.tsv` — same format, grouped by campaign
- `NEGATIVES-REVIEW-REQUIRED.md` — ambiguous terms needing human
  review with context (the neighbouring converting queries, current
  keyword matches)

### Report Structure

1. **Recovery Summary** — total wasted spend by theme, monthly
   extrapolation, count of negatives per theme
2. **Theme Breakdown** — one section per theme with top 20 terms, spend,
   match type recommendation
3. **Flagged for Review** — ambiguous terms with context
4. **Protection List** — existing converting queries that new negatives
   must not block (audit this before applying)
5. **Rollout Plan** — which negatives to apply first (lowest risk,
   highest recovery), which to apply after a 7-day hold

## Hard Rules

- **Never block a query that has ≥ 1 conversion in the period.** Even
  if it's in an Empleo / Informacional bucket, a converting variant
  overrides the theme classification.
- **Protection list is mandatory** — output the converting-query list
  so the human operator can sanity-check before applying.
- **Phrase before Exact** when the theme has many variants — Exact
  requires too many entries for broad themes.
- **Competitor negatives require explicit brief authorisation** —
  comparative queries often convert at low volumes but high rates
  for challenger brands.
- When `min_spend_threshold` excludes < 80% of terms, flag that the
  threshold is too loose for the account volume.
- **Never recommend `broad match negative`** — Google deprecated best
  practice for this; Phrase/Exact cover every real case.
