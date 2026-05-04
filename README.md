# claude-marketing-skills

A collection of [Claude Code](https://claude.com/claude-code) skills, agents,
and scripts for performance marketing work — paid ads audits, SEO analysis,
HubSpot CRM hygiene, attribution checks, and dashboard reporting.

These were built to run an in-house agency workflow over Google Ads, Meta
Ads, LinkedIn Ads, Google Search Console, GA4, and HubSpot. They are
shared here so other marketers, freelancers, and agencies can adapt them.

> **What is a skill?** A markdown file with frontmatter that Claude Code
> auto-loads. When the user says something matching the skill's
> `description`, Claude follows the SKILL.md as a procedure. See the
> [Claude Code skills docs](https://docs.claude.com/claude-code/skills).

## What's inside

### `skills/` — 34 skills

**Paid ads — Google**
- `google-ads-deep-audit` — 50-check systematic review of a Google Ads account
- `google-ads-anomaly-diagnostic` — diagnose sudden spend / conversion shifts
- `google-ads-ad-copy-writer` — generate RSAs aligned with brand + landing page
- `google-ads-negative-keyword-builder` — mine search terms for negatives
- `google-ads-cannibalization-check` — find keywords competing across campaigns
- `google-ads-dayparting-analysis` — hour-of-day / day-of-week bid recommendations

**Paid ads — Meta**
- `meta-ads-deep-audit` — 50-check Meta Ads account review
- `meta-ads-dayparting-analysis` — Meta delivery hour analysis
- `meta-ads-frequency-recommendations` — frequency caps + creative refresh signals

**Paid ads — LinkedIn**
- `linkedin-ads-deep-audit` — LinkedIn Ads account review

**Paid ads — cross-channel**
- `ads-audit` — quick cross-channel audit
- `ads-budget-review` — budget pacing + reallocation recommendations
- `ads-creative-audit` — creative fatigue + winner detection
- `ads-pacing-monitor` — month-to-date pacing alerts
- `ads-strategy-plan` — quarterly paid strategy planning
- `ab-test-design` — design statistically valid A/B tests
- `ppc-math` — common PPC calculations (CPA, ROAS, LTV, target CPMs)
- `competitor-teardown` — competitor ads + landing page teardown

**SEO**
- `seo-technical-audit` — Core Web Vitals + crawlability technical audit
- `seo-schema-audit` — structured data audit
- `seo-images-audit` — image optimization audit
- `seo-local-audit` — local SEO + Google Business Profile audit
- `seo-ai-search-readiness` — readiness for AI search (ChatGPT, Perplexity, Gemini)
- `landing-page-audit` — conversion + on-page SEO landing page audit

**Google Search Console**
- `gsc-weekly-report` — weekly GSC performance report
- `gsc-indexing-audit` — indexation issues + priority triage
- `gsc-cannibalization-check` — query/page cannibalization detection
- `gsc-content-opportunities-page2` — page 2 keyword opportunities

**HubSpot**
- `hubspot-funnel-audit` — funnel stage + lifecycle audit
- `hubspot-attribution-audit` — multi-touch attribution health check
- `hubspot-ads-reconciliation` — reconcile ad clicks vs HubSpot contacts
- `hubspot-linkedin-form-sync` — LinkedIn Lead Gen Forms → HubSpot sync audit

**Reporting + ops**
- `dashboard-builder` — build a client dashboard snapshot
- `memory-update` — maintain per-client memory (state + log files)

### `agents/` — 10 specialist agents

Sub-agents invokable from a skill or directly:
`audit-budget`, `audit-compliance`, `audit-creative`, `audit-google`,
`audit-hubspot`, `audit-linkedin`, `audit-meta`, `audit-seo`,
`audit-tracking`, `business-analyst`.

### `references/`

Shared reference docs the skills read for context:
- `benchmarks-spain.md` — paid + organic benchmarks for the Spanish market
- `compliance-eu-spain.md` — EU + Spain advertising compliance notes
- `platform-specs.md` — current ad platform creative specs

### `scripts/seo/`

Standalone Python helpers used by SEO skills:
- `pagespeed_check.py` — PageSpeed Insights v5 + CrUX combined check
- `crux_history.py` — CrUX History API trend analysis
- `fetch_page.py` — page fetcher with SSRF guard
- `parse_html.py` — basic HTML parsing helpers
- `seo_credentials.py` — env-var-based API key reader

Install: `pip install -r scripts/seo/requirements.txt`
Set: `export GOOGLE_PAGESPEED_API_KEY=...`

## Installation

**Project-scoped** (recommended — only Claude Code in this repo sees them):
```bash
git clone https://github.com/<you>/claude-marketing-skills.git
cd your-project
mkdir -p .claude
ln -s "$(pwd)/../claude-marketing-skills/skills" .claude/skills
ln -s "$(pwd)/../claude-marketing-skills/agents" .claude/agents
```

**User-scoped** (every Claude Code session sees them):
```bash
git clone https://github.com/<you>/claude-marketing-skills.git ~/.claude-marketing-skills
ln -s ~/.claude-marketing-skills/skills ~/.claude/skills
ln -s ~/.claude-marketing-skills/agents ~/.claude/agents
```

Restart Claude Code after linking.

## Important: MCP server dependency

Most skills reference an internal MCP server with tools like
`get_gsc_pages`, `get_google_ads_search_terms`, `get_hubspot_deals`, etc.

These tool names are **not implemented in this repo** — you need to either:
1. Build your own MCP server exposing equivalent tools (Google Ads API,
   GSC API, Meta Marketing API, LinkedIn Ads API, HubSpot API), or
2. Adapt the skills to call official APIs / CLIs / scrapers directly, or
3. Use the skills as **prompt templates** and feed data manually.

The procedures, audit checklists, severity tiers, and output formats
inside each SKILL.md are the actual reusable IP. The MCP tool calls are
plumbing you'll swap for your own data layer.

## Sanitization notes

Originally these skills referenced specific agency clients. All client
names have been replaced with placeholders (`ContentCo`, `LeadGenCo`,
`SaaSCo`, `WellnessBrand`, `RetailCo`, `CamperCo`, `AviationCo`). The
business-context examples are kept because they illustrate why severity
weighting differs by sector — adapt them to your own clients.

No credentials, API keys, OAuth tokens, internal URLs, or proprietary
implementation code are included. The MCP server itself is not published.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Issues + PRs welcome. If you build a new skill in this style, send it
over.
