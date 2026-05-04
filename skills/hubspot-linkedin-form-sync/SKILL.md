---
name: hubspot-linkedin-form-sync
description: >
  Reconcile LinkedIn Lead Gen form fills against HubSpot contacts tagged as
  LinkedIn-sourced. Detects the "leak" — LinkedIn-reported leads that never
  land in the CRM — which inflates LinkedIn's platform CPL and hides real
  unit economics. Produces a per-campaign leak rate, root-cause hypotheses
  (webhook failure, UTM missing, hidden form field, dedupe), and a remediation
  plan. Activate when user says "LinkedIn lead leak", "HubSpot LinkedIn
  reconciliation", "LinkedIn form sync", "why are LinkedIn leads missing in
  HubSpot", "true LinkedIn CPL", or "LinkedIn vs HubSpot contact counts".
---

# HubSpot ↔ LinkedIn Form Sync Audit

Diagnoses why LinkedIn-reported lead counts disagree with HubSpot
contact counts tagged as LinkedIn-sourced. The gap is the **leak** —
leads LinkedIn billed you for but the CRM never received, or received
under a different source label. Leak percentage directly inflates
LinkedIn's platform-reported CPL vs true HubSpot-denominator CPL.

## Required Inputs

- `client_id` (required)
- `date_range_start` / `date_range_end` — default last 90 days (needs
  enough volume to see campaign-level leaks clearly)
- `tolerance_pct` (optional) — acceptable leak threshold. Default `10`.
  Leaks below this are flagged as "within noise".

## Client Brief

Read `clients/briefs/<client_id>.md`, `clients/state/<client_id>.md`,
and top 10 entries of `clients/logs/<client_id>.md`:

- Confirm LinkedIn Ads is configured (`client.linkedin_ads`).
- Confirm HubSpot is configured + `primary_entity` (contact-centred is
  typical for lead-gen clients like SaaSCo).
- Check `source_normalization` for LinkedIn entries (`linkedin`,
  `linkedin-ads`, `LinkedIn`) — missing entries fragment the count.
- Check `extra_contact_properties` for `hs_object_source_detail_1` or
  `record_source_detail_1` — needed for form-level granularity.

## Data Collection (MCP tools, parallel)

1. `get_linkedin_ads_lead_gen_performance` — LinkedIn-reported form
   fills per campaign (`leads`, `form_opens`, `qualified_leads`).
2. `get_linkedin_ads_campaign_performance` — LinkedIn spend + clicks
   per campaign (for leak-weighted CPL math).
3. `get_hubspot_source_attribution` entity=`contact` dimension=`utm_source`
   — HubSpot-counted contacts grouped by source (post-normalization).
4. `get_hubspot_source_attribution` entity=`contact` dimension=`hs_analytics_source`
   — corroborating original-touch source.
5. `get_hubspot_source_attribution` entity=`contact` dimension=`utm_campaign`
   — HubSpot contacts per campaign label (joins to LinkedIn campaign names
   via `campaign_aliases`).
6. `get_hubspot_contacts` filtered by `utm_source=linkedin` (and any
   raw LinkedIn variants in source_normalization, looped) with
   `limit=10000` — verify exact count matches aggregated attribution.

Check response `warnings[]` — if HubSpot returned `total_matching >
row_count`, the base counts are a lower bound and this skill must
emit a confidence caveat.

## Reconciliation Logic

### Step 1 — per-campaign LinkedIn-reported count

From step 1 data, for each LinkedIn campaign:
```
linkedin_reported_leads[campaign] = leads (from lead gen performance)
```

### Step 2 — per-campaign HubSpot-landed count

From step 5 data, join HubSpot `utm_campaign` values to LinkedIn
campaign names via `campaign_aliases`. For each LinkedIn campaign:
```
hubspot_landed[campaign] = sum of contacts for aliased utm_campaign values
```

If no alias configured → use exact utm_campaign match + flag as
"needs campaign_alias entry".

### Step 3 — leak per campaign

```
leak_count = linkedin_reported - hubspot_landed
leak_pct   = leak_count / linkedin_reported * 100

linkedin_platform_cpl = spend / linkedin_reported          # what LinkedIn shows
hubspot_true_cpl      = spend / hubspot_landed             # the real number
cpl_inflation_pct     = (linkedin_platform_cpl - hubspot_true_cpl) / hubspot_true_cpl * 100
```

### Step 4 — leak severity

| Severity | Criterion |
|---|---|
| **Critical** | leak_pct > 50 on spend ≥ €500 |
| **High** | leak_pct 25–50 on spend ≥ €500, OR leak_pct > 50 on spend €100–500 |
| **Medium** | leak_pct 10–25 on spend ≥ €500 |
| **Low** | leak_pct < 10 (within noise) |
| **Over-count** | hubspot_landed > linkedin_reported (sanity-flag — investigate; usually means HubSpot is aggregating Lead Gen Forms + website-direct submissions both tagged linkedin) |

## Root-Cause Hypotheses

For each campaign with `Medium+` severity, rank these hypotheses by
evidence:

| Hypothesis | Evidence to check |
|---|---|
| **LinkedIn Lead Gen → HubSpot webhook / sync broken** | HubSpot contacts list shows no recent LinkedIn-sourced contacts for dates where LinkedIn recorded fills. Ask client to verify LinkedIn ↔ HubSpot native integration or middleware (Zapier, Make) health. |
| **UTM parameters not set on Lead Gen thank-you redirect** | LinkedIn Lead Gen forms don't carry UTMs by default. Leads land in HubSpot with `utm_source` = null → bucket as "unknown" not "linkedin". Check source_attribution on `hs_analytics_source` — contacts may show up as PAID_SOCIAL there but not utm_source. |
| **Source normalization missing a raw variant** | Raw `utm_source` values found in `get_hubspot_source_attribution` (e.g. `linkedin-ads`, `LI`, `linkedin_sponsored`) not mapped in `source_normalization`. Flag + emit patch. |
| **Campaign alias missing** | HubSpot has the contact but its `utm_campaign` value doesn't resolve to the LinkedIn campaign name via `campaign_aliases`. Landed count per-campaign = 0 even though overall linkedin count matches. Fix = add alias regex. |
| **Dedupe on email** | Repeat form fills by existing contact don't create new HubSpot records — LinkedIn counts every fill, HubSpot counts distinct contacts. Expected leak ~5–15% for warm audiences / retargeting campaigns. |
| **Hidden form field capture broken** | If LinkedIn Lead Gen uses hidden fields to inject UTM/campaign into the submission, check form config. If hidden fields aren't being pulled into HubSpot contact properties, all leads land as "unknown". |
| **Lead magnet disqualifies** | Some form submissions trigger HubSpot workflows that archive/delete contacts as spam → LinkedIn counts them, HubSpot doesn't keep them. Rare but visible via `hs_lead_status`. |

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-linkedin-form-sync/`:

- `FORM-SYNC-REPORT.md` — primary report
- `FORM-SYNC-CAMPAIGNS.tsv` — per-campaign: linkedin_reported, hubspot_landed,
  leak_count, leak_pct, platform_cpl, true_cpl, cpl_inflation_pct, severity

First non-empty line of `FORM-SYNC-REPORT.md`:

```
LEAK_PCT: <overall>% SEVERITY: <critical|high|medium|low> CLIENT: <client_id> PERIOD: <start>..<end> TRUE_CPL: €<amount> vs PLATFORM_CPL: €<amount>
```

### Report Structure

1. **TL;DR** — overall leak %, CPL inflation %, top 3 campaigns by leak severity
2. **Per-campaign table** — sorted by leak severity × spend
3. **Ranked hypotheses** — per high/critical campaign, most likely root cause
   with specific evidence cited
4. **Remediation plan** — ordered actions:
   a. Config patches (copy-paste-ready JSON additions for
      `source_normalization` and `campaign_aliases` in the client file)
   b. HubSpot workflow / integration checks to run with client
   c. UTM / hidden-field fixes on the LinkedIn Lead Gen form
5. **True unit economics** — CPL recalculated with HubSpot denominator,
   per-campaign and overall. Clearly labelled as "the real number" vs
   LinkedIn's platform-reported CPL.
6. **Confidence caveats** — any HubSpot truncation warnings, missing
   campaign aliases, or unmapped source variants that bound the
   certainty of the finding.

## Hard Rules

- **Never trust LinkedIn-reported CPL for client reporting.** Platform
  CPL is always inflated by the leak. Use HubSpot-denominator CPL.
- **The leak cannot be resolved by the MCP server alone.** Most root
  causes require client-side action (webhook fix, UTM config, HubSpot
  workflow audit). Skill output is a diagnosis + action plan, not a
  self-healing fix.
- **Config patches must be exact JSON** — operator should be able to
  paste into `clients/<id>.json` without editing.
- **When `source_normalization` coverage is incomplete** (raw LinkedIn
  variants not mapped), flag this as the FIRST hypothesis to fix —
  other diagnoses can't be trusted until normalization is clean.
- **Over-count findings** (HubSpot > LinkedIn) are usually a sign the
  client runs multiple LinkedIn lead paths (Lead Gen forms + organic
  website tracked as LinkedIn referral). Split into clean sub-sources
  via additional normalization before declaring a bug.
- **Emit confidence caveat** when any HubSpot response has truncation
  warnings or when campaign_aliases coverage is < 80%.
