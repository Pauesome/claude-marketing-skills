---
name: hubspot-attribution-audit
description: >
  Attribution audit of HubSpot leads and deals: source mix, UTM hygiene,
  original vs latest-touch crosstab, and canonical campaign roll-up. Detects
  labelling gaps (leads marked "-", "null", or left blank), source
  normalization coverage, and paid-then-outbound / outbound-then-paid
  conversion patterns. Activate when the user says "attribution audit", "UTM
  hygiene", "source mix review", "where are my leads coming from", or
  "original vs latest touch".
---

# HubSpot Attribution Audit — Spain

Cross-platform attribution audit that answers three questions:

1. **Where are leads / deals actually coming from?** (after source_normalization)
2. **How clean is UTM tagging?** (offline / null / "-" share, unrecognized sources)
3. **Did paid drive the first touch, the last touch, or both?** (original × latest crosstab)

All semantics come from the client's `hubspot.source_normalization`,
`hubspot.campaign_aliases`, and `hubspot.offline_markers` config — not
hardcoded here.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 90 days
- Fail fast on missing input; no mid-audit prompts.

## Client Brief

Read `clients/briefs/<client_id>.md` before collecting data. Use it to
interpret source patterns: LeadGenCo's phone-call leads labelled `-`/`null` are
expected (older demographic, calls the website phone); SaaSCo's LinkedIn
outbound mixed with paid Google is a different story. Sector determines
what "healthy UTM hygiene" looks like.

## Data Collection (MCP Tools, parallel)

1. `get_hubspot_source_attribution` with `dimension: "utm_source"` — primary attribution dimension
2. `get_hubspot_source_attribution` with `dimension: "utm_campaign"` — raw utm_campaign distribution
3. `get_hubspot_source_attribution` with `dimension: "hs_analytics_source"` — HubSpot-tracked original source
4. `get_hubspot_source_attribution` with `dimension: "record_source_detail_1"` — form-level attribution (if configured in extra_contact_properties)
5. `get_hubspot_source_attribution` with `dimension: "web_source"` — landing page (when extra_deal_properties declares it)
6. `get_hubspot_original_vs_latest` — first-touch × last-touch crosstab
7. `get_hubspot_campaign_performance` — canonical campaign roll-up

## Audit Dimensions & Weights

| Dimension | Weight | Primary data source |
|---|---|---|
| UTM Hygiene | 30% | `get_hubspot_source_attribution` (any dimension) |
| Source Normalization Coverage | 20% | `source_normalization` config vs raw values |
| Campaign Alias Coverage | 20% | `campaign_aliases` config vs raw utm_campaign values |
| Original vs Latest Patterns | 20% | `get_hubspot_original_vs_latest` |
| Revenue Attribution Clarity | 10% | `get_hubspot_campaign_performance` |

## Critical Checks (severity × 3.0)

- **HA-CT1** Offline / unlabelled share < 30% of total leads (else UTM instrumentation broken)
- **HA-CT2** Source normalization mapping covers ≥ 80% of raw values (else map is stale)
- **HA-CT3** `hs_analytics_source` populated on ≥ 90% of contacts (else HubSpot tracking script missing on some pages)
- **HA-CT4** When `campaign_aliases` is configured, ≥ 70% of raw utm_campaign values resolve to canonical names
- **HA-CT5** Won deals have a populated `utm_source` on ≥ 80% of rows (revenue without attribution = blind spot)

## Full Check List

### UTM Hygiene (30%)
- **HA-UH1** Offline / null / "-" share by dimension listed explicitly
- **HA-UH2** Top 10 unrecognized `utm_source` values flagged (not in source_normalization map)
- **HA-UH3** `utm_medium` populated consistently (cpc / paid_social / email / referral)
- **HA-UH4** `utm_campaign` present on ≥ 80% of paid-source contacts
- **HA-UH5** Forms collecting `record_source_detail_1` (extra_contact_properties declares it) — populated rate ≥ 90%
- **HA-UH6** No `utm_source` values contain spaces or unusual casing without a normalization rule

### Source Normalization Coverage (20%)
- **HA-NC1** List raw values not in `hubspot.source_normalization` — these silently pass through as their own group
- **HA-NC2** Recommend additions to `source_normalization` for the top 10 unmapped values
- **HA-NC3** Verify that normalized `google`, `meta`, `linkedin` buckets exist and are populated
- **HA-NC4** No conflicting mappings (same raw → different canonical)

### Campaign Alias Coverage (20%)
- **HA-CA1** For clients with `campaign_aliases`: report which raw values resolved and which fell through
- **HA-CA2** List top 10 raw utm_campaign values not matched by any rule
- **HA-CA3** Recommend regex additions for unmatched patterns (show pattern + proposed canonical)
- **HA-CA4** Verify alias rules evaluate in sensible order (most-specific first, generic last — first match wins)
- **HA-CA5** Meta adset-as-campaign cases specifically checked if brief indicates Meta is active

### Original vs Latest Patterns (20%)
- **HA-OL1** Diagonal cells (original == latest) vs off-diagonal share — off-diagonal = multi-touch journeys
- **HA-OL2** Notable off-diagonal cells: paid → organic, organic → paid, paid → outbound, outbound → paid
- **HA-OL3** Revenue distribution across crosstab — single-touch vs multi-touch revenue share
- **HA-OL4** For SaaSCo: paid-first → outbound-close share = outbound team assist rate
- **HA-OL5** Last-touch attribution bias acknowledged when reporting ROAS to the client

### Revenue Attribution Clarity (10%)
- **HA-RA1** Top 10 canonical campaigns by revenue — documented with raw_aliases
- **HA-RA2** `avg_cycle_days` per canonical campaign — cycle length reasonable
- **HA-RA3** Campaign-to-won ratio consistent across canonicals (else one campaign is drawing in different-quality leads)

## Scoring

Each check → PASS / WARNING / FAIL. Critical checks × 3.0. Normalize per
dimension → weighted average → overall score.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-hubspot-attribution-audit/`:

- `HUBSPOT-ATTRIBUTION-REPORT.md` — findings + action list
- `HUBSPOT-UTM-GAPS.md` — unmapped raw values with recommended mappings
- `HUBSPOT-ORIGINAL-VS-LATEST.md` — full crosstab table

First non-empty line of `HUBSPOT-ATTRIBUTION-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: hubspot PERIOD: <start>..<end>
```

Then sections:

1. **Source Mix Snapshot** — normalized source table (contacts, deals, won, revenue)
2. **UTM Hygiene Gaps** — offline share, null share, unmapped values, unresolved campaigns
3. **Original vs Latest Crosstab** — full 2-D table with revenue per cell
4. **Canonical Campaign Performance** — canonical_campaign table with raw_aliases
5. **Recommended Mappings** — proposed additions to `source_normalization` and `campaign_aliases`
6. **Quick Wins** — UTM instrumentation fixes < 1 hour
7. **Action List** — Critical → High → Medium → Low

## Non-Negotiables

- Never hardcode "expected" source distributions — baseline is the client's
  own prior period
- Always surface the offline / null share explicitly (not buried in "other")
- Alias-map recommendations must include the exact regex pattern to paste
  into `clients/<id>.json`
- When offline share > 30%, recommend website form instrumentation fixes
  first — do NOT recommend shifting budget away from paid based on apparent
  CVR until attribution is cleaned up
