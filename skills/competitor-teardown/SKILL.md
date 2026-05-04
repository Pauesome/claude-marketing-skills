---
name: competitor-teardown
description: >
  Systematic competitive landing-page analysis. Fetches a competitor URL,
  dissects positioning, messaging hierarchy, objection handling, trust
  signals, CTA strategy, and pricing presentation. Produces a scored
  teardown and strategic recommendations for how our client should
  differentiate. Different from landing-page-audit (which audits the
  client's own page) — this skill looks outward. Activate when the user
  says "competitor teardown", "analyse this competitor", "teardown of
  [URL]", "how are they positioned", "competitive positioning", or pastes
  a competitor URL and asks for analysis.
---

# Competitor Teardown — Spain

Fetches and analyses a competitor landing page to surface positioning
choices, persuasion tactics, and differentiation opportunities for our
client. Cross-channel — applies to Google Ads LPs, Meta LPs, LinkedIn
LPs, and SEO pages equally.

## Required Inputs

- `client_id` (required) — so the recommendation section can contrast
  the competitor against **this** client's positioning
- `competitor_url` (required) — fully qualified URL to the competitor
  landing or home page
- `page_context` (optional) — what role the page plays (Google Ads
  brand landing, Meta lead-gen LP, homepage, product page). If
  omitted, inferred from URL structure.

Fail fast on missing URL or client_id.

## Client Brief

Read `clients/briefs/<client_id>.md` to extract **our** client's:

- Value proposition and differentiation angles
- Sector compliance constraints (what our client CAN'T say — e.g.
  Special Ad Category restrictions, Ley 16/2011 disclosures for
  credit products)
- Target audience and objections
- Existing positioning language

Recommendations should contrast the competitor's positioning with
**this** client's positioning — not produce generic "how to market"
advice.

## Data Collection

1. **WebFetch** the `competitor_url` — the only data source required.
   Extract:
   - Full visible copy (headline, sub-headline, body, bullets)
   - CTA text and placement (above-fold, mid-page, sticky)
   - Trust signals (logos, testimonials, case studies, certifications,
     ratings, counts)
   - Pricing (if shown) and pricing framing (monthly vs annual, free
     trial, money-back)
   - Form fields (for lead-gen pages)
   - Navigation structure and footer links (to understand product
     portfolio)

2. **Optional: WebFetch** one or two sub-pages if linked from the main
   page and relevant (e.g. pricing page, product page, about page).
   Don't cascade; keep fetch count low.

## Teardown Framework

### 1. Value Proposition Decomposition

| Question | What to extract |
|---|---|
| What problem do they solve? | Pain language, problem agitation |
| Who is their ICP? | Explicit callouts, industry/role signals |
| What transformation do they promise? | Before/after, outcomes, results |
| What's their unique mechanism? | Proprietary method, tech, process |

### 2. Messaging Hierarchy

| Element | Evaluation |
|---|---|
| **Headline** | Clarity, benefit-driven, specific vs vague, character count |
| **Sub-headline** | Expands "how", reinforces UVP, supports headline |
| **Body copy** | Framework used (AIDA/PAS/BAB), benefit-to-feature ratio |
| **CTA** | Verb + value, visibility, friction (form length, steps), variant count |
| **Trust** | Logos, testimonials count, rating platforms, certifications, case studies |

### 3. Objection Handling

Identify objections the page explicitly addresses:
- Price objection (too expensive? too cheap?)
- Risk objection (money-back, free trial, guarantee)
- Complexity objection (setup time, integration)
- Trust objection (years in business, number of clients, certifications)
- "Why now" objection (urgency, scarcity, limited offer)

For each objection, note how the competitor addresses it. **Missing
objections = differentiation opportunity** for our client.

### 4. Spain / EU Compliance Check

Flag any claims that would be non-compliant in Spain / EU context:
- Unsupported superlatives ("el mejor", "el único", "100%
  garantizado") — Ley General de Publicidad
- Financial-product claims without disclosure (APR, risk warnings) —
  Ley 16/2011
- Health / medication claims — Ley 29/2006
- Cookie / consent violations visible in the page — AEPD

These aren't competitor weaknesses we should copy; they're things our
client **must avoid** even if the competitor is doing them.

## Scoring Rubric (100 points)

| Category | Max | Criteria |
|---|---|---|
| Positioning clarity | 15 | Problem + ICP + differentiation immediately clear |
| Headline effectiveness | 15 | Benefit-driven, specific, scannable |
| Copy quality | 15 | Benefits > features, readable, persuasive structure |
| CTA strategy | 15 | Action-oriented verb, value in CTA, low-friction |
| Trust signals | 10 | Quality and quantity of social proof |
| Visual hierarchy | 10 | Flow, emphasis on key elements |
| Objection handling | 10 | Pre-empts top 3 objections |
| Pricing presentation | 5 | Clear, justified, anchored |
| Brand voice | 5 | Consistent, memorable, fits ICP |

## Output

Write to `./reports/<client_id>/<YYYY-MM-DD>-competitor-teardown/<competitor_slug>/`:

- `COMPETITOR-TEARDOWN.md` — primary report (with SCORE header)
- `COMPETITOR-COPY-CAPTURE.md` — verbatim copy of headline, sub,
  body, CTA, trust (for reference; do not copy into our client's
  materials)

First non-empty line of `COMPETITOR-TEARDOWN.md`:

```
COMPETITOR: <domain> SCORE: <0-100>/100 CLIENT: <client_id> URL: <full_url>
```

### Report Structure

1. **Executive Summary** — one paragraph. Overall score, headline
   takeaway, top 3 positioning moves this competitor is making
2. **Value Proposition Decomposition** — four-question table
3. **Messaging Hierarchy** — element-by-element evaluation
4. **Objection Handling** — table of common objections × whether the
   competitor addresses them (Yes / No / Partially)
5. **Trust Signal Inventory** — specific counts and examples (e.g.
   "12 customer logos, 4 testimonials with name+photo+company, 4.7★
   rating from 2,341 Google reviews")
6. **Compliance Observations** — any Spain/EU-risky claims our client
   should explicitly **not** copy
7. **Differentiation Opportunities for <client_id>** — specific
   positioning / copy / trust-signal moves our client could make
   based on competitor gaps AND our client's actual strengths (from
   brief)
8. **Do-Not-Copy List** — competitor tactics that would violate
   compliance in our client's sector

## Hard Rules

- **Never recommend copying competitor copy verbatim** — the entire
  purpose of this teardown is to find differentiation, not imitation.
- **Never recommend a claim our client is not authorised to make**
  from the brief — even if the competitor makes it. Financial
  Special Ad Category rules apply to us even if competitors ignore
  them.
- **Always root differentiation recommendations in the client's
  actual strengths** (from brief), not just "do the opposite of
  competitor". Opposite-ism without substance is a weak strategy.
- **Compliance observations are read-only** — don't suggest
  competitor violations as "things we should do too". Flag them so
  the operator knows the competitor is cutting corners that our
  client shouldn't.
- **When the fetched page has minimal text** (e.g. JS-rendered SPA
  where WebFetch only sees skeleton HTML), state this explicitly
  and recommend a manual review — don't infer positioning from an
  empty page.
