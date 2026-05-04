---
name: google-ads-cannibalization-check
description: >
  Detect query-level cannibalization inside a Google Ads account — the same
  search term triggering ads from multiple campaigns or ad groups, splitting
  auction data, inflating CPCs, and breaking Smart Bidding's learning.
  Produces a query-routing fix (which campaign should own the query) and a
  negative-keyword plan to enforce it. Activate when the user says "google
  ads cannibalization", "campaigns competing", "brand cannibalizing
  non-brand", "which campaign should own", or asks why two campaigns bid
  on the same term.
---

# Google Ads Cannibalization Check — Spain

Finds cases where a single user query is matched by ad groups in ≥ 2
campaigns (or ≥ 2 ad groups in the same campaign), which dilutes
conversion signal, inflates CPCs via internal auction, and confuses
Smart Bidding. Outputs a **query-routing plan**: which campaign should
own each cannibalized query, and what negatives enforce the routing.

Distinct from `gsc-cannibalization-check` — that skill handles organic
page-level cannibalization; this one handles paid-ad campaign-level
cannibalization.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 60 days (need
  volume to identify recurring patterns)
- `min_shared_spend` (optional) — minimum EUR spend on a query across
  all campaigns to consider it. Default `€20`.

Fail fast on missing inputs.

## Client Brief

Read `clients/briefs/<client_id>.md`. Key signals:

- **Brand vs non-brand separation strategy** — most cannibalization
  stems from non-brand campaigns matching brand queries. Brief should
  say which campaigns are brand-only.
- **Multi-location or multi-product structure** — clients with parallel
  campaigns per product (e.g. LeadGenCo's lead-product vs Renta Vitalicia)
  often have legitimate overlap that is NOT cannibalization. Brief
  should flag acceptable overlap.
- **PMax presence** — PMax campaigns consume queries from Search
  campaigns silently; flag as a specific cannibalization class.

If brief is missing, still run but mark all findings as "needs human
triage" — can't distinguish legitimate overlap from cannibalization
without context.

## Data Collection (MCP Tools)

1. `get_google_ads_search_terms` (most important):
   - `limit: 1000`
   - `min_spend: 0`
   - period from inputs
   - Returns which campaign / ad group each search term was served in

2. `get_google_ads_keywords` — for keyword-level overlap detection
   (different from search-term overlap)

3. `get_google_ads_campaign_performance` — to tag each cannibalized
   campaign with its bid strategy, campaign type, and target (needed
   for routing recommendation)

## Cannibalization Logic

A query is a **cannibalization candidate** when:

- Same search term appears in ≥ 2 (campaign, ad_group) pairs
- Combined spend across campaigns ≥ `min_shared_spend`
- At least one campaign has conversions on the term OR total
  impressions ≥ 500

For each candidate, compute:

| Field | How |
|---|---|
| `query` | The search term |
| `competing_entities` | Every (campaign, ad_group) that served the query + their spend, clicks, impressions, conversions |
| `total_spend_at_stake` | Sum of spend across competing entities |
| `winner_candidate` | Entity with highest conversions; if tied, best CPA; if still tied, highest CTR |
| `cannibalization_class` | One of: Brand→NonBrand leak, PMax→Search leak, Product overlap, Match-type overlap (Exact vs Broad), Geo overlap |

## Cannibalization Classes (ordered by common severity)

### 1. Brand → Non-Brand leak
Non-brand campaigns matching brand queries. Nearly always a bug — the
non-brand campaign serves lower-quality copy and lower-converting LPs,
and the brand campaign loses conversion signal.

**Fix**: add brand terms as campaign-level negatives (Phrase match) to
every non-brand campaign. Leave brand campaign untouched.

### 2. PMax → Search leak
PMax serves ads for queries that a Search campaign already bids on.
PMax wins the auction at a cheaper-looking CPA (steals credit for
converting queries the Search campaign trained).

**Fix**: add the leaked queries to PMax campaign-level negatives (only
possible via Google Ads support or via the 2024 "campaign negative
keywords for PMax" feature). Alternatively, add brand exclusions.

### 3. Product overlap
Two Search campaigns (e.g. "lead-product" and "Renta Vitalicia")
match the same generic query ("vender casa manteniendo uso"). Brief
must decide which campaign owns generic queries.

**Fix**: determine the winning campaign via brief + conversion data,
add the query as negative to the losing campaign.

### 4. Match-type overlap
Same campaign, ad group A has `"keyword"` (Phrase) and ad group B has
`[keyword exact]` (Exact). Expected behaviour: Exact should win. If
data shows Phrase ad group serving the Exact query, the ad group
structure is broken — Exact keyword is paused / low-QS / different
campaign priority.

**Fix**: ensure the Exact match lives in the higher-priority ad group;
add `-[keyword exact]` as negative on the Phrase ad group.

### 5. Geo overlap
Two campaigns both target Spain but with different geo bids (e.g. one
for Madrid, one for rest-of-Spain). Queries from Madrid can serve either.

**Fix**: use Presence targeting (not Presence or Interest) and verify
location exclusions are symmetric.

## Severity

- **High**: Brand → Non-Brand leak with ≥ €100 shared spend / month,
  OR PMax → Search leak on converting queries
- **Medium**: Product overlap with ≥ €50 shared spend, OR match-type
  overlap where Exact is losing
- **Low**: Geo overlap, OR product overlap < €50 shared spend

## Scoring

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: google_ads PERIOD: <start>..<end>
```

Score = 100 − (`cannibalization_spend` / `total_account_spend` × 200),
capped to [0, 100]. A 10% cannibalization rate = 80/100 (C grade).

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-ads-cannibalization/`:

- `ADS-CANNIBALIZATION-REPORT.md` — primary report (with SCORE header)
- `ADS-CANNIBALIZATION-MATRIX.tsv` — query × campaign matrix with
  spend/conversions per cell
- `ADS-ROUTING-PLAN.md` — the recommended query-routing decisions and
  specific negative keywords to enforce them, grouped by losing campaign

### Report Structure

1. **Executive Summary** — cannibalization spend as % of total spend,
   count by class, score
2. **Top 20 Cases** — one block per query with:
   - Query
   - Competing entities table (campaign, ad_group, spend, conv, CPA)
   - Cannibalization class
   - Recommended winner + rationale
   - Enforcement negatives (exact keywords to add, where)
3. **Systemic Patterns** — e.g. "non-brand campaigns missing brand
   negatives → account-level shared negative list recommended"
4. **Copy-Paste Negatives** — consolidated list grouped by destination
   (account shared list / campaign level / ad group level)

## Hard Rules

- **Brand queries on non-brand campaigns are always cannibalization**
  unless the brief explicitly authorises (rare — only for awareness-
  stage campaigns that intentionally catch brand queries without a
  brand campaign).
- **Never recommend pausing a campaign as the fix** — always recommend
  query routing via negatives. Pausing loses the routing logic and
  creates new gaps.
- **PMax cannibalization of Search requires brand exclusions**, not ad
  group negatives — PMax doesn't accept ad-group-level negatives.
- **Do not flag query overlap as cannibalization when brief authorises
  it** (e.g. deliberately running two LP variants on different
  campaigns as an experiment). Route those findings to
  `ab-test-design` instead.
- When Smart Bidding is enabled on competing campaigns, Smart Bidding
  will re-route some queries automatically — flag that fixing
  structural cannibalization still helps (Smart Bidding performs
  better with clearer signal separation).
