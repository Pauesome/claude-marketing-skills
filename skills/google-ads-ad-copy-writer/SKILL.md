---
name: google-ads-ad-copy-writer
description: >
  Write or improve Google Ads RSA headlines and descriptions for a specific
  campaign or ad group. Produces intent-matched copy variants, Spanish-native
  (not machine-translated), compliance-aware for regulated sectors (financial
  services Special Ad Category, healthcare LOPDGDD Art. 9, consumer credit
  Ley 16/2011). Activate when the user says "write ad copy", "RSA headlines",
  "improve my ads", "new ad copy for [campaign]", "ad copy ideas", or
  references a specific campaign needing creative refresh.
---

# Google Ads Ad Copy Writer — Spain

Produces Spanish-native Responsive Search Ads (RSAs) calibrated to the
searcher's intent, the client's business model, and EU/Spain compliance.
This is a **producer skill** — outputs copy-paste-ready headlines and
descriptions, not a diagnostic report.

## Required Inputs

- `client_id` (required)
- `campaign_id` OR `ad_group_id` OR `campaign_name_contains` — at least
  one scope filter required. Refuse to run "generic ad copy" without a
  target ad group / campaign.
- `intent` (optional) — one of `brand`, `non-brand`, `competitor`,
  `informational`, `transactional`. Default: infer from top keywords in
  the ad group.

Fail fast on missing scope. Never write "generic" RSAs.

## Client Brief

Read `clients/briefs/<client_id>.md` and extract:

- Sector (financial services → Special Ad Category; healthcare → LOPDGDD
  Art. 9; consumer credit → Ley 16/2011 disclosures; medicamentos →
  Ley 29/2006 restrictions)
- Language: always Spanish unless brief says otherwise. Never
  machine-translate English headlines — rewrite natively.
- Value proposition, differentiators, customer objections
- Prohibited claims (e.g. LeadGenCo: cannot imply "reverse mortgage";
  SaaSCo: cannot promise specific ranking outcomes)
- Target audience age/demographic (critical for tone — LeadGenCo's 60–80 y.o.
  audience needs trust-building copy, not youth-marketing hype)

If the brief is missing, refuse to produce copy. Generic Spanish RSAs
without brief context are low quality.

## Data Collection (MCP Tools)

Run in parallel:

1. `get_google_ads_campaign_performance` scoped to the target campaign(s)
   — current CTR, CPC, conversion rate
2. `get_google_ads_keywords` scoped to the target ad group — top
   keywords by impressions (these tell you the exact searcher intent)
3. `get_google_ads_search_terms` scoped to the target campaign
   — real queries users typed (source of authentic language patterns)

Before writing:
- Dedupe search terms, filter to `≥ 10 impressions`
- Identify the top 10 intent patterns (transactional verbs, comparison
  terms, specific features) — these must appear in headlines
- Check current RSA Ad Strength if available in campaign data

## Copy Generation Rules

### Structural
- 15 headlines per RSA (30 chars max each)
- 4 descriptions per RSA (90 chars max each)
- Pin strategically: headline 1 = brand or primary value prop; all
  others unpinned (Google's tests show minimal pinning = better CTR)
- No duplicate value props across headlines — each headline earns its slot

### Intent Framework (match headline style to intent)

| Intent | Headline angle | Example pattern |
|---|---|---|
| Brand | Reassure + direct to action | "Oficial: [Brand] — Más Info Aquí" |
| Non-brand / high-intent | Specific feature + CTA | "Hipoteca Inversa desde 3%" |
| Comparison | Direct comparison + differentiator | "Más que una Hipoteca Inversa" |
| Informational | Answer the question | "¿Qué es la lead-product?" |
| Competitor | Named alternative + advantage | "Alternativa a [Competitor]" |

### Must-haves in every RSA
- ≥ 1 headline contains the primary keyword of the ad group (exact match
  is fine when natural — Google will insert DKI if needed)
- ≥ 1 headline contains a specific CTA verb (Solicita, Descubre,
  Calcula, Consulta, etc.)
- ≥ 1 headline contains a trust signal (años, clientes, sin
  compromiso, gratuito)
- ≥ 1 description contains the value prop + differentiator
- ≥ 1 description contains an explicit CTA
- Correct Spanish typographic standards: ¿? ¡! opening punctuation,
  accented characters, no English anglicisms unless intentional

### Must-NOT-have
- Claims that require compliance footnotes that don't fit ("0%
  comisión*", "garantizado", "el mejor")
- Superlatives without evidence ("el más barato", "el número uno")
- Age-based targeting in copy for Special Ad Category clients (implied
  age exclusion = policy violation even if the creative is compliant)
- Emoji unless brief explicitly authorises
- ALL CAPS HEADLINES (policy violation)
- Duplicate words across ≥ 3 headlines (Google deduplicates → lower Ad
  Strength)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-ad-copy/<campaign_or_adgroup_slug>/`:

- `RSA-COPY.md` — one section per intent variant with:
  - Ad group / campaign it targets
  - Intent classification
  - 15 headlines + character counts
  - 4 descriptions + character counts
  - Pinning recommendation
  - Rationale: which searcher intent each headline addresses
- `RSA-COPY.tsv` — tab-separated format for direct paste into Google
  Ads Editor (columns: Ad group, Headline 1–15, Description 1–4, Path 1,
  Path 2, Final URL)

Do **not** emit a `SCORE:` header — this is a producer, not an auditor.

## Hard Rules

- Never produce English-translated headlines. If the brief says Spanish,
  write Spanish from scratch.
- Never exceed character limits. If the idea doesn't fit, rewrite shorter
  — don't truncate mid-word.
- For financial services, healthcare, credit, and medicamentos clients,
  include a top-of-output section: **Compliance Checklist** — list the
  EU/Spain rules that apply and confirm each headline satisfies them.
- When the brief or search terms reveal a customer objection (e.g.
  "es una estafa", "riesgo"), write at least one headline that directly
  neutralises it — do not ignore objections.
- Refuse to produce ad copy when conversion tracking is broken for the
  target campaign. Copy doesn't help an unmeasured campaign; fix
  tracking first.
