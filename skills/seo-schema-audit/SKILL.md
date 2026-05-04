---
name: seo-schema-audit
description: >
  Detect, validate, and recommend JSON-LD structured data on a Spanish
  client's site. Covers Organization, LocalBusiness, RealEstateAgent,
  Service, Product, FAQ, Article, BreadcrumbList. Validates against
  schema.org and Google's rich-result eligibility rules. Activate when
  the user says "schema audit", "JSON-LD", "structured data", "rich
  results", "Google rich snippets", or "validate schema".
---

# SEO Schema Audit — Spain

Diagnostic + generative audit that answers: **does each money page emit
the right structured data, and is it valid for Google rich results?**
Schema is the cheapest E-E-A-T signal a site can ship — but ~70% of
Spanish lead-gen sites either omit it, ship the wrong type, or hand-roll
broken JSON.

## Required Inputs

- `client_id` (required) — uses `client.gsc.site_url` to resolve the host
- `urls` (optional) — explicit list to audit. If omitted: top-10 pages
  by clicks (from `get_gsc_pages`) + the homepage.
- `expected_types` (optional, from brief) — sector defaults:
  - real-estate / mortgage → `Organization` + `RealEstateAgent` +
    `Service` + `FAQPage` + `BreadcrumbList`
  - SaaS / B2B → `Organization` + `Product` or `SoftwareApplication` +
    `FAQPage` + `Article` (blog)
  - local services → `LocalBusiness` (or specific subtype) + `Service`
    + `FAQPage`

Fail fast on missing input.

## Client Brief

Read `clients/briefs/<client_id>.md` + state + top-10 logs. Brief sets
expected types per page-template. Without it, fall back to inferring
from URL pattern (`/blog/` → Article, `/servicios/` → Service, etc.) and
flag the inference in the report so the next session can codify it in
the brief.

## Data Collection

### Per-URL
```bash
python3 scripts/seo/fetch_page.py <url> --output reports/.../<slug>.html
python3 scripts/seo/parse_html.py reports/.../<slug>.html --json > reports/.../<slug>-parsed.json
```

`parse_html.py` returns all detected schema blocks (JSON-LD, Microdata,
RDFa) plus title / meta / H1 for context.

### Per-page validation
For each detected JSON-LD block:
1. JSON parse — catches syntax errors that Google silently ignores
2. `@context` must be `https://schema.org` (warn on `http://`)
3. `@type` must be a known schema.org type — reject custom types
4. Required-property check by type (see table below)
5. Recommended-property check (warn-only)
6. Cross-block consistency — multiple blocks on the same page should
   agree on `Organization`, `name`, `url`, `logo`

## Required-property matrix

| Type | Required | Recommended |
|---|---|---|
| `Organization` | `name`, `url` | `logo`, `sameAs[]`, `contactPoint`, `address` |
| `LocalBusiness` (or subtype) | `name`, `address`, `telephone` | `openingHoursSpecification`, `geo`, `priceRange`, `image` |
| `RealEstateAgent` | `name`, `url`, `address` | `areaServed`, `image`, `aggregateRating` |
| `Service` | `serviceType`, `provider` | `areaServed`, `description`, `offers` |
| `Product` | `name`, `image`, `offers` | `aggregateRating`, `review`, `brand`, `gtin/sku` |
| `FAQPage` | `mainEntity[]` (≥ 2) | each `Question` needs `name` + `acceptedAnswer.text` |
| `Article` / `BlogPosting` | `headline`, `author`, `datePublished` | `image`, `dateModified`, `publisher` |
| `BreadcrumbList` | `itemListElement[]` (≥ 2) | each item needs `position`, `name`, `item` |

## Scoring

Per inspected URL: PASS (all expected types present + valid) = 100,
WARNING (present but missing recommended fields, or one expected type
missing) = 50, FAIL (no schema, or invalid JSON, or wrong type) = 0.
Average across URLs. A homepage missing `Organization` caps the grade
at C — that's the foundation block.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-seo-schema-audit/`:

- `SEO-SCHEMA-REPORT.md` — primary report
- `<slug>-parsed.json` per URL — raw parse output
- `recommended-schemas/<slug>.json` — generated JSON-LD for any URL
  that's missing an expected type (ready to drop into the page)

First non-empty line of `SEO-SCHEMA-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: site PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — coverage matrix (URL × expected types),
   score, top-3 missing
2. **Per-URL Findings** — detected types vs expected, validation errors
3. **Generated Recommendations** — for each missing schema, paste-ready
   JSON-LD pre-filled with values pulled from page parse (title,
   description, canonical, etc.)
4. **Cross-Page Inconsistencies** — `Organization.name` differs between
   homepage and blog, etc.
5. **Rich-Result Eligibility** — by type, what blocks Google's
   eligibility (e.g. `FAQPage` policy: only on FAQ-pattern pages, not
   navigation accordions)

## Hard Rules

- **Never auto-generate `aggregateRating`** unless the brief confirms
  the site has real review data. Fake ratings are a manual-action risk.
- **`FAQPage` is no longer eligible for rich results in Google for
  non-government / non-medical sites** (since Aug 2023). Recommend it
  for AI-search citation, not for SERP rich snippet, and label clearly.
- **Only emit `Article` schema on actual articles**, not on listing
  pages or pillar pages. Listing → `CollectionPage` or `ItemList`.
- **Use `@id` to link blocks** (`{"@id": "https://example.com/#org"}`)
  when a page has multiple blocks referring to the same entity. Don't
  duplicate `Organization` inside every block.
- **Don't recommend `BreadcrumbList`** if the visual UI doesn't show
  breadcrumbs — Google requires the on-page presence.
