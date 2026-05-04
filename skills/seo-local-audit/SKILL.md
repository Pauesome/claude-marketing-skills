---
name: seo-local-audit
description: >
  Local SEO audit for Spanish service-area or storefront clients. Checks
  Google Business Profile signals, NAP consistency across the site,
  LocalBusiness / RealEstateAgent schema, citation footprint via free
  OpenStreetMap (Overpass) lookups, and review/rating surface area.
  Activate when the user says "local SEO", "GBP audit", "Google
  Business Profile", "NAP", "citaciones locales", "ficha Google", or
  references a service-area / storefront business.
---

# SEO Local Audit — Spain

Diagnostic audit that answers: **does this client surface in local
intent searches (`abogado madrid`, `inmobiliaria barcelona`, "near me")
and does its on-site footprint reinforce its GBP profile?** Specific to
businesses with a physical location or a defined service area.

This skill is gated: only run if the brief flags `local_business: true`
(or sector matches: real-estate, legal, medical, restaurant, retail,
service-area trades).

## Required Inputs

- `client_id` (required)
- `name`, `address`, `phone`, `website` — pulled from
  `clients/briefs/<client_id>.md` (canonical NAP). Audit fails fast if
  the brief doesn't define them — local SEO without a canonical NAP is
  meaningless.
- `service_areas` (optional, list) — cities/regions covered. Default:
  derive from address city + 30km radius.

## Client Brief

Read brief + state + top-10 logs. Extract:
- Canonical NAP (Name, Address, Phone)
- Operating hours
- Service categories (single vs multi-location)
- Existing GBP listing URL (if known) — `place_id` if available
- Known review platforms (Google, Trustpilot, idealista, fotocasa, etc.
  for Spanish real-estate)

## Data Collection

### Site-level (run once)

```bash
# Homepage + footer + contact page — usually carry NAP
python3 scripts/seo/fetch_page.py <site_url>                     --output reports/.../home.html
python3 scripts/seo/fetch_page.py <site_url>/contacto            --output reports/.../contact.html
python3 scripts/seo/parse_html.py reports/.../home.html --json  > reports/.../home-parsed.json
python3 scripts/seo/parse_html.py reports/.../contact.html --json > reports/.../contact-parsed.json
```

Search the parsed text + schema for occurrences of `name`, `address`,
`phone` from the brief — capture each match with its surrounding 200-
char context for the report.

### NAP scan across all internal pages (sampled)

Pull top-30 pages by clicks via `get_gsc_pages`. Fetch each, scan for
NAP mentions (regex on phone format `+?\d{2,3}\s?\d{3}\s?\d{3}\s?\d{3}`,
postal-code format `\b\d{5}\b`, etc.). Output a coverage table.

### Citation footprint (free, no paid APIs)

Use Overpass (OpenStreetMap) — free, no key:

```
GET https://overpass-api.de/api/interpreter
[out:json];
node["name"~"<client_name>"]
  (around:50000, <lat>, <lng>);
out;
```

Find the canonical city's lat/lng via the Nominatim API (also free,
unauthenticated, rate limit = 1 req/s). Document any matching OSM
nodes — these tend to mirror real-world citations (yellow pages, GBP
extracts, Apple Maps source data).

### GBP profile (manual, no API access)

We don't have GBP API keys (paid tier). Skill instead instructs the
user to perform a manual check and paste the output back: photo count,
review count, average rating, last post date. Document these inputs in
`reports/.../gbp-manual-input.md` for future reuse.

## Checklist

| Check | Pass |
|---|---|
| Homepage shows full NAP | name + address + phone all visible |
| Footer carries NAP on every page | sampled pages all have it |
| `LocalBusiness` (or specific subtype) schema present | yes, with `address`, `telephone`, `geo` |
| Schema NAP matches brief NAP | exact-string match (allowing trivial whitespace) |
| `openingHoursSpecification` schema | present, ≥ 1 day defined |
| `geo.latitude` + `geo.longitude` | present |
| `sameAs[]` includes GBP profile URL | present, valid |
| Phone is `tel:` linked | `<a href="tel:...">` present |
| Contact page reachable from homepage in ≤ 2 clicks | yes |
| Address embedded as Google Maps iframe (or static map) | present on contact page |
| OSM citation present | at least 1 OSM node found within 50km |
| Multi-location: each location has own page | per-brief location count = page count |
| GBP manual: ≥ 5 photos | yes |
| GBP manual: ≥ 25 reviews | yes |
| GBP manual: avg rating ≥ 4.0 | yes |
| GBP manual: post in last 90 days | yes |

## Scoring

Per check: PASS=100, WARNING=50, FAIL=0. Average. Specific caps:
- NAP mismatch between brief and site → cap C
- No `LocalBusiness` schema at all → cap C
- GBP manual inputs missing → cap B (skill ran without the data)
- Any phone number on site that doesn't match brief NAP → cap C (NAP
  inconsistency is the cardinal local-SEO sin)

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-seo-local-audit/`:

- `SEO-LOCAL-REPORT.md` — primary
- `nap-coverage.csv` — page × NAP-element matrix
- `osm-citations.json` — Overpass response
- `gbp-manual-input.md` — operator-supplied inputs (or template if
  unfilled)
- `recommended-localbusiness-schema.json` — JSON-LD draft using brief
  NAP, ready to drop into the page

First non-empty line of `SEO-LOCAL-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: site PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — score, grade, top-3 issues
2. **NAP Consistency** — brief canonical vs site occurrences, per-page
   coverage, any mismatches highlighted in red
3. **Schema Coverage** — what's present, what's missing, generated
   draft for the gaps
4. **GBP Snapshot** (manual) — photos, reviews, posts, recommendations
   on what to update
5. **Citation Footprint** — OSM matches + recommendation list of
   Spanish citation sites to claim/audit (Páginas Amarillas, idealista,
   fotocasa, infoempleo, Doctoralia, etc. — pick by sector from brief)
6. **Service-area / Multi-location Plan** — per-location page audit
7. **Recommendations** — ordered by impact, with file/edit hints

## Hard Rules

- **Skip this skill entirely** if the brief doesn't flag local. SaaS,
  pure e-commerce, and remote-only consultancies don't need it.
- **NAP must come from the brief, not the site.** If they conflict,
  the brief is the contract — the site is what's broken.
- **Don't recommend specific paid citation services** (e.g. Yext,
  BrightLocal, Whitespark) without checking the brief — the agency may
  have a vendor preference.
- **GBP API requires a Google business verification** that the agency
  doesn't have for the client. Don't pretend otherwise — the manual
  check is the truth source until paid integration exists.
- **Overpass is rate-limited** (~10k queries/day, no key). One query
  per audit is fine; don't loop.
- **Spanish-specific citation sites** worth mentioning by sector:
  real-estate → idealista + fotocasa + pisos.com; legal → mundojuridico
  + Confilegal; medical → Doctoralia; restaurants → TheFork + ElTenedor.
  Don't include these blindly — pick from the brief.
