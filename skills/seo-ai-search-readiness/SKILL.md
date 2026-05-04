---
name: seo-ai-search-readiness
description: >
  Audit a Spanish client's site for AI-search citability: ChatGPT,
  Perplexity, Google AI Overviews, Claude. Checks AI-crawler access,
  llms.txt + llms-full.txt presence, content extractability, citation
  signals, brand-mention surface area, and structured-data coverage.
  Activate when the user says "AI search", "AI Overviews", "GEO",
  "llms.txt", "ChatGPT citation", "Perplexity SEO", or "AI visibility".
---

# SEO AI-Search Readiness — Spain

Diagnostic audit that answers: **when an AI search engine answers a
question in this client's space, will it cite this site?** Different
ranking surface from Google blue links — ranking factors are heavier on
authority signals (brand mentions, schema, source clarity) and content
extractability (clean HTML, no JS-only content, citable claims).

This is the 2025+ paradigm. Most Spanish clients have zero coverage
here.

## Required Inputs

- `client_id` (required) — uses `client.gsc.site_url`
- `prompts` (optional, list of strings) — natural-language questions to
  test brand mention recall. If omitted, generate from brief: top-5
  product/service queries the client wants to win on.

Fail fast on missing `client_id`.

## Client Brief

Read brief + state + top-10 logs. Brief identifies:
- the client's core entities (products, services, brand)
- competitor brands (we want to know who AI cites instead)
- whether the site has any expertise/author bylines (E-E-A-T anchors)

## Data Collection

### Site-level checks (run once)

```bash
python3 scripts/seo/fetch_page.py <site_url>/llms.txt        # presence + content
python3 scripts/seo/fetch_page.py <site_url>/llms-full.txt   # presence + content
python3 scripts/seo/fetch_page.py <site_url>/robots.txt      # AI-crawler rules
python3 scripts/seo/fetch_page.py <site_url>                 # homepage HTML
python3 scripts/seo/parse_html.py <homepage.html>            # schema, author, sameAs
```

### Per-page checks (top 10 by clicks)

For each URL:
1. `python3 scripts/seo/fetch_page.py <url> --user-agent "Mozilla/5.0"`
2. Repeat with `--user-agent "GPTBot/1.0"` and `--user-agent "PerplexityBot/1.0"`
   to detect any divergent rendering / cloaking
3. `parse_html.py` to extract: H1, sub-headings, schema blocks, author
   byline, last-modified date, internal-link count, citable-claim count
   (rough heuristic: list items + numbered facts)

### Brand-mention surface (qualitative)

For each prompt in `prompts`, ask Claude (this conversation) to
self-answer the prompt without browsing — then compare whether the
client's brand surfaces. This is a directional signal, not a
benchmark. Document each prompt + Claude's answer + whether brand
appeared in `reports/.../brand-mention-test.md`.

## Checklist

| Check | Pass |
|---|---|
| robots.txt explicitly allows GPTBot | not blocked, OR no specific rule (default-allow) |
| robots.txt allows Google-Extended | same |
| robots.txt allows ClaudeBot | same |
| robots.txt allows PerplexityBot | same |
| robots.txt allows CCBot (Common Crawl) | same |
| `/llms.txt` present | 200, content present |
| `/llms-full.txt` present | 200, content present |
| Server-rendered content (no JS-only) | `<main>` content extractable from raw HTML |
| `Organization` schema with `sameAs[]` (≥ 3 social/wiki links) | present |
| Author byline on content pages | byline + `Person` schema or visible name |
| `dateModified` or visible last-update | present |
| Citable claims linked to sources | external citations or footnotes detectable |
| HTTPS + canonical | both present |
| Per-prompt brand mention | brand cited by Claude unaided |

## Scoring

Per check: PASS=100, WARNING=50, FAIL=0. Average across all applicable.
Brand-mention recall counts as one weighted check (worth 3× normal).
- llms.txt + llms-full.txt both missing → cap at B (Google AI Overviews
  doesn't require them yet, but Perplexity and indexed-LLM caches favor
  them)
- Any AI crawler explicitly blocked in robots.txt → cap at C (the brief
  must explicitly state "block AI crawlers" to override)
- JS-only content on >50% of audited pages → cap at C

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-seo-ai-search-readiness/`:

- `SEO-AI-SEARCH-REPORT.md` — primary
- `brand-mention-test.md` — prompts × answers × cited?
- `recommended-llms-txt.md` — generated `/llms.txt` candidate, ready to
  copy to the site root
- `recommended-llms-full-txt.md` — generated `/llms-full.txt` candidate,
  built from the top-10 audited pages

First non-empty line of `SEO-AI-SEARCH-REPORT.md`:

```
SCORE: <0-100>/100 GRADE: <A|B|C|D|F> CLIENT: <client_id> PLATFORM: site PERIOD: <start>..<end>
```

### Report Structure

1. **Executive Summary** — overall grade, top-3 missing signals
2. **AI Crawler Access Matrix** — bot × allow/block, with line ref
3. **llms.txt Coverage** — present/missing, with generated draft
4. **Content Extractability** — JS-rendering risk per page, with raw
   HTML weight comparison
5. **Authority Signals** — schema coverage, author bylines, sameAs
6. **Brand Mention Recall** — prompt-level results, list of competitors
   cited instead
7. **Recommendations** — ordered by impact

## Hard Rules

- **Never recommend blocking AI crawlers** unless the brief explicitly
  asks for paywall/subscription protection. Default 2026 stance: allow.
- **`llms.txt` is not standard yet.** Phrase the recommendation as
  "emerging standard, low-cost to publish, hedges against future
  retrieval pipelines." Don't oversell it.
- **Brand-mention recall via Claude self-test is anecdotal.** Single
  prompt = anecdote, 5+ prompts = directional, 20+ prompts = signal.
  Don't claim AI-search ranking from a 1-prompt test.
- **Don't fabricate `sameAs[]` URLs**. If the brief doesn't list social
  profiles, recommend creating + linking, don't invent.
- **JS-rendered content** can still be cited if rendered via Googlebot
  + indexed. Distinguish "AI crawler can't fetch" from "content invisible
  to LLM training" — they're different problems with different fixes.
