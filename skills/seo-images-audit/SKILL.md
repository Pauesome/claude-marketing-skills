---
name: seo-images-audit
description: >
  Image SEO audit for a Spanish client's site. Inspects alt text quality,
  file weight, modern formats (WebP / AVIF), lazy-loading, dimensions,
  and decorative-vs-content classification. Activate when the user says
  "image SEO", "alt text audit", "image optimization", "image weight",
  or "WebP migration".
---

# SEO Images Audit — Spain

Diagnostic audit that answers: **are images on the site helping or
hurting CWV + accessibility + organic image traffic?** Heavy hero images
inflate LCP; missing alt text wastes ranking signal and accessibility;
non-WebP delivery costs bandwidth.

## Required Inputs

- `client_id` (required) — uses `client.gsc.site_url` to resolve host
- `urls` (optional) — pages to audit. Default: top-10 pages by clicks
  (last 28d via `get_gsc_pages`) + homepage
- `max_images_per_page` (optional, default 30) — hard cap to avoid
  audit blowup on gallery pages

Fail fast on missing input.

## Client Brief

Read brief + state + top-10 logs. Brief identifies:
- which pages are paid-campaign LPs (LCP failures here are critical)
- which pages are blog/content (image SEO matters more for organic
  image search)
- whether the site has an editorial team that can fix alt text in bulk

## Data Collection

Per URL:
```bash
python3 scripts/seo/fetch_page.py <url> --output reports/.../<slug>.html
python3 scripts/seo/parse_html.py reports/.../<slug>.html --json > reports/.../<slug>-parsed.json
```

`parse_html.py` extracts every `<img>` tag with: `src`, `alt`, `width`,
`height`, `loading` attribute, `srcset`, `sizes`. For `<picture>`, the
chosen `<source>` formats are reported.

For each unique image URL across all pages, fetch HEAD (not GET — saves
bandwidth) to capture:
- `Content-Length`
- `Content-Type`
- `Cache-Control`

Use `fetch_page.py --head` (or extend with a `--method HEAD` flag if not
present yet — see Hard Rules below).

## Checklist (per image)

| Check | Pass |
|---|---|
| `alt` present | non-empty unless image is purely decorative (`role="presentation"` or empty alt by design) |
| `alt` length 5–125 chars | within range when present |
| `alt` not generic | not "image", "imagen", "foto", "picture", filename-like, or repeated across page |
| `width` + `height` attributes | both present (prevents CLS) |
| `loading="lazy"` on below-fold | present unless image is LCP-eligible |
| LCP image NOT lazy | top-fold hero must NOT be `loading=lazy` |
| Modern format | `image/webp` or `image/avif` (jpeg/png on transparent assets ok) |
| File weight | ≤ 200 KB for content images, ≤ 80 KB for thumbnails, ≤ 500 KB for hero |
| `srcset` for responsive | present when intrinsic width > 800 |

## Per-page rollup

- **alt-coverage** = images with valid alt / total images
- **modern-format-share** = WebP/AVIF / total
- **avg-weight** = sum(KB) / count
- **LCP-image** = first image with `priority`, `fetchpriority=high`, or
  position in DOM above-fold (estimated from index)

## Scoring

Weighted average of per-image checks → per-page score.
- alt-coverage < 50% → page caps at C
- LCP image > 500 KB → page caps at C
- Any single image > 1 MB → page caps at D

Final score = mean(per-page).

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-seo-images-audit/`:

- `SEO-IMAGES-REPORT.md` — primary report
- `images-per-page.csv` — every image × every page, with all extracted
  attrs + HEAD response data, sortable
- `top-offenders.md` — heaviest 20 images across the site, with the
  page they appear on and a "convert to webp + resize to <w>x<h>"
  recommendation each

First non-empty line of `SEO-IMAGES-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: site PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — overall score, top-3 quick wins
2. **Per-page table** — score, image-count, alt-coverage, modern-format
   share, avg-weight, LCP-image weight
3. **Alt Text Issues** — empty / generic / too-long, with page+selector
4. **CLS Risks** — images missing width/height
5. **LCP Risks** — heavy hero images, lazy-loaded LCP candidates
6. **Format Migration Plan** — count of jpeg/png that should be WebP
7. **Tooling recommendation** — `cwebp -q 80 …` example, or sharp/imgix
   wrapper if the brief mentions a build pipeline

## Hard Rules

- **Don't recommend AVIF on a site without a build pipeline** that can
  generate it — it's not a copy-paste optimization. WebP is the safe
  default.
- **Don't suggest auto-generating alt text via AI in production**
  without a human review step. Wrong alt text = accessibility regression.
- **Decorative images (CSS backgrounds, role="presentation")** are
  excluded from the alt-coverage denominator. Don't pad the score.
- **Image-heavy galleries** (>30 images on one page) are sampled, not
  exhaustively audited. Note the sample size in the report.
- If `fetch_page.py` lacks a HEAD mode, fall back to `requests.head` via
  a one-off inline Python snippet — don't extend `fetch_page.py` mid-
  audit. Track the gap as a follow-up in `clients/logs/<id>.md`.
