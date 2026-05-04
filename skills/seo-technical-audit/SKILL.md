---
name: seo-technical-audit
description: >
  Technical SEO audit for a Spanish client's site. Checks robots.txt,
  XML sitemap, security + cache headers, JS rendering, AI-crawler access
  rules (GPTBot / Google-Extended / ClaudeBot / PerplexityBot), Core Web
  Vitals (PSI + CrUX), and indexability signals. Activate when the user
  says "technical SEO", "technical audit", "is my site crawlable",
  "core web vitals", "robots.txt", or "sitemap audit".
---

# SEO Technical Audit — Spain

Diagnostic audit that answers: **can Google (and AI bots) actually crawl,
render, and index this site, and how fast does it feel to a real user?**
Distinct from `gsc-indexing-audit` (which inspects already-discovered
URLs) — this skill operates one level up, on the site infrastructure that
gates discovery.

## Required Inputs

- `client_id` (required) — client must have `gsc` configured (provides
  `site_url`)
- `urls` (optional) — explicit list of pages to deep-test for CWV. If
  omitted, sample top-10 pages by clicks from `get_gsc_pages` (last 28d).
- `GOOGLE_PAGESPEED_API_KEY` env var (required for the PSI / CrUX checks
  — without it the script skips that section and emits a warning, no
  mid-audit prompt).

Fail fast on missing input.

## Client Brief

Read `clients/briefs/<client_id>.md` + `state/<client_id>.md` + top 10 of
`logs/<client_id>.md`. The brief tells you which pages drive revenue
(paid-campaign landing pages, Hipoteca Inversa angle for LeadGenCo) — score
those harder. Sector also matters: a real-estate site with `disallow: /`
is critical; a static brochure site less so.

## Data Collection

The skill mixes raw HTTP fetches (the vendored `scripts/seo/*.py`
helpers) with our own MCP tools when relevant.

### Per-site checks (run once)

```bash
python3 scripts/seo/fetch_page.py <site_url>/robots.txt --output reports/.../robots.txt
python3 scripts/seo/fetch_page.py <site_url>/sitemap.xml --output reports/.../sitemap.xml
```

If `sitemap.xml` 404s, also try `/sitemap_index.xml`. Then re-run
`fetch_page.py <site_url>` against the homepage to capture HTTP headers
(stored in `reports/.../homepage-headers.txt` — `fetch_page.py` writes
the response headers as a sidecar by design).

### Per-URL checks (top 10 pages)

For each URL:
1. `inspect_gsc_urls({ urls: [...] })` (our MCP tool) — capture
   `verdict`, `robots_txt_state`, `page_fetch_state`,
   `crawled_as`, `last_crawl_time`
2. `python3 scripts/seo/pagespeed_check.py <url> --strategy both --json`
   — PSI lab + CrUX field for both mobile and desktop
3. `python3 scripts/seo/parse_html.py <fetched_html>` — extract
   `<title>`, meta description, canonical tag, hreflang count, schema
   count, internal-link count, presence of `<noscript>` content (signals
   client-side rendering)

## Checklist

| Check | Source | Pass condition |
|---|---|---|
| robots.txt reachable + valid syntax | fetch_page | 200, no parse errors |
| robots.txt does NOT block site | parse | no global `Disallow: /` |
| AI crawlers allowed where expected | parse | per brief — default = allow GPTBot, Google-Extended, ClaudeBot, PerplexityBot, CCBot, Applebot-Extended |
| sitemap.xml present + reachable | fetch_page | 200, valid XML |
| sitemap referenced in robots.txt | parse | `Sitemap:` line present |
| sitemap last-mod recent | parse | most recent `<lastmod>` ≤ 30d |
| HTTPS + valid cert | fetch_page | scheme=https, no redirect chain to http |
| HSTS header | fetch_page | `Strict-Transport-Security` present, `max-age >= 15552000` |
| `X-Content-Type-Options: nosniff` | fetch_page | header present |
| `X-Frame-Options` or CSP frame-ancestors | fetch_page | header present |
| Cache-Control on static-looking paths | fetch_page | non-empty for HTML, long max-age for static assets |
| Gzip/Brotli enabled | fetch_page | `Content-Encoding: gzip\|br` |
| Per-URL CWV PASS (mobile) | pagespeed_check | LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 |
| Per-URL Google can fetch + index | inspect_gsc_urls | verdict=PASS, no robots block |
| `<noscript>` content present on JS-heavy pages | parse_html | flag if site is SPA AND noscript empty |

## Scoring

Per check: PASS = 100, WARNING = 50, FAIL = 0. Average across all
applicable checks. CWV failures on a paid-landing-page (per brief) cap
the grade at C. `Disallow: /` in production robots.txt = automatic F.

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-seo-technical-audit/`:

- `SEO-TECHNICAL-REPORT.md` — primary report
- `robots.txt`, `sitemap.xml`, `homepage-headers.txt` — raw artifacts
- `cwv-per-url.json` — full PSI + CrUX dump per inspected URL
- `_raw-inspect.json` — `inspect_gsc_urls` raw response

First non-empty line of `SEO-TECHNICAL-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: site PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — score, grade, top-3 critical findings
2. **Crawlability** — robots.txt + sitemap + AI-crawler matrix
3. **Security & Headers** — HTTPS, HSTS, nosniff, frame-options, CSP
4. **Performance (Core Web Vitals)** — per-URL CWV table (LCP / INP /
   CLS, mobile + desktop, lab + field), worst-3 offenders highlighted
5. **Indexability per top-URL** — table from `inspect_gsc_urls` joined
   with PSI verdict
6. **JS Rendering Risks** — pages with empty `<noscript>` and low
   crawled-as-mobile rendered HTML weight
7. **Recommendations** — ordered by severity, each with file path or
   header to change

## Hard Rules

- **Quota**: PSI free tier = 25k calls/day. Use `--strategy both` for
  10 URLs = 20 calls — safe.
- **Never recommend disallowing AI crawlers globally.** Block specific
  high-cost paths (e.g. `/admin`, `/checkout`) only if brief says so.
- **CWV without field data is a lab estimate.** If CrUX has no data for
  a URL (origin-level only), say so explicitly — don't dress lab numbers
  as field measurements.
- **Don't recommend HTTP/2 or HTTP/3 upgrades** unless the brief says
  the host controls the CDN. Hosting-platform decisions aren't actionable
  by the client.
- Skip security-header checks on paths the brief flags as third-party
  (Hubspot forms iframes, etc.) — they have their own headers.
