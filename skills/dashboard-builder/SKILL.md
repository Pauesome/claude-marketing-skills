---
name: dashboard-builder
description: >
  Build a snapshot dashboard for a Spanish client and publish it to the
  Postgres-backed Vercel app. Orchestration-only: the heavy lifting is in
  scripts/build-dashboard-snapshot.ts (data) and scripts/save-dashboard-snapshot.ts
  (push). The skill picks parameters, reads context, runs the scripts,
  and writes the qualitative narrative. Activate when the user says "build
  dashboard", "client dashboard", "looker dashboard", "performance dashboard",
  "weekly dashboard", or "dashboard for <client>".
---

# Dashboard Builder

Lightweight orchestrator that runs two canonical scripts and adds
interpretation. **Do not write ad-hoc TS for fetch / aggregate / push
logic** — the scripts are deterministic and version-controlled. If you
need behavior the scripts don't support, either flag it as a limitation
or extend the script in a separate session (don't fork inline).

## Required Inputs

- `client_id` (required) — confirm via `list_clients`.
- `date_range_end` — default today (system-provided current date).
- `date_range_start` — default `date_range_end − 365 days`.
- `pipeline` (optional) — pipeline key. Defaults to `is_default: true`.
- `publish_to_db` (optional, default `true`) — push snapshot to Postgres
  for the dashboard-app to render. Requires `DATABASE_URL` env var.

No mid-skill prompts. Fail fast on missing required inputs.

## Step 1 — Three-file context load

Always read all three before doing anything else (project rule):

1. `clients/briefs/<client_id>.md` — sector, products, KPIs, sales-cycle
2. `clients/state/<client_id>.md` — current campaigns, blockers
3. Top 10 entries of `clients/logs/<client_id>.md` — recent context

This shapes:
- Whether the chosen window is sensible given sales cycle (LeadGenCo's
  90–150d cycle means a 28-day window misses most of the funnel).
- Which warnings to escalate vs treat as routine.
- The narrative voice in `DASHBOARD-NOTES.md`.

## Step 2 — Build the snapshot (canonical script)

Run from the project root:

```bash
DATA_MODE=live npx tsx scripts/build-dashboard-snapshot.ts \
  --client <client_id> \
  --start <YYYY-MM-DD> \
  --end <YYYY-MM-DD> \
  --out ./reports/<client_id>/<YYYY-MM-DD>-dashboard/
```

Outputs:
- `data.json` — V2 daily-resolution snapshot blob (the file you'll push).
- `DASHBOARD-NOTES.md` — skeleton with SCORE header, coverage stats,
  warnings list, and a "Hosted dashboard" placeholder.
- `_raw-*.json` — raw MCP responses for debugging.

The script's stdout is a JSON summary: `{ ok, distinct_sources,
distinct_campaigns, total_leads, total_spend, warnings_count, data_path }`.
Capture it. If `ok: false` or it crashes, surface the error verbatim
and stop — don't attempt repairs.

## Step 3 — Populate commentary (optional but recommended)

Before pushing the snapshot, edit `data.json` to add interpretation
into the `commentary` block. This is the value the skill adds beyond
what the script can compute.

The script seeds an empty commentary:
```json
{
  "commentary": {
    "summary": "",
    "recommendations": []
  }
}
```

Replace with real content. `summary` is markdown (paragraphs separated
by blank lines). `recommendations` is an array; each item has a
`title`, `body` (markdown), and `priority` (`high` | `medium` | `low`).

Tie the content to what the script wrote in `DASHBOARD-NOTES.md`:
- The summary mirrors the "Highlights" section but condensed for inline
  display.
- Recommendations come from cross-skill insights — budget reallocation
  (use `ads-budget-review` if applicable), creative refresh
  (`ads-creative-audit`), source attribution gaps
  (`hubspot-attribution-audit`), etc. If you have output from other
  audits this period, summarize their actionable items here.
- Reference URL filters when relevant: a recommendation about the
  meta source's CPL spike can link to
  `?sources=meta&start=2026-04-01` so the reader lands on the relevant
  view directly.

Edit the JSON file directly — `jq` or a small node one-liner works,
just keep the schema valid.

## Step 4 — Push to Postgres

```bash
npx tsx scripts/save-dashboard-snapshot.ts \
  --client <client_id> \
  --data ./reports/<client_id>/<YYYY-MM-DD>-dashboard/data.json
```

Skip this step (with a warning in `DASHBOARD-NOTES.md`) if
`DATABASE_URL` is not set. Never block local artifacts on a missing
DB connection.

The script's stdout is `{ ok, run_date, dashboard_url }`. The
`dashboard_url` field is the live dashboard URL (built from
`VERCEL_DASHBOARD_BASE_URL` env var); use it in the next step.

## Step 5 — Append narrative to DASHBOARD-NOTES.md

The script-written notes are mechanical (counts, warnings, URL).
Append your interpretation as additional sections:

- **Highlights** — 3–5 bullets calling out the most important findings.
  Numbers from `kpis` + sources detail. Tie to brief context (sector
  benchmarks, sales-cycle expectations).
- **Anomalies** — anything that needs human attention this week. Big
  CPL movement, source-mix shift, unmatched campaigns with material
  spend, low qualification rate vs prior cohorts.
- **Action items** — concrete next steps tied to the dashboard view.
  Link to specific filters (`?sources=meta` or `?start=2026-04-01`)
  rather than describing in prose.
- **Hosted dashboard URL** — replace the script's placeholder with the
  actual URL captured in step 3, plus 1–2 lines explaining what to
  click first.

## Step 6 — Update memory

After the dashboard is live, invoke `/update-memory` for the client.
Surface decisions made this run (window chosen, anomalies surfaced,
follow-ups scheduled). Don't duplicate the dashboard's data —
memory captures the *meta* (decisions / context), not the metrics.

## Hard Rules

- **CRM is the source of truth.** Conversions = HubSpot stage marker
  counts only. The script enforces this; never inject platform-reported
  conversion data into KPIs.
- **No ad-hoc fetch / aggregate code.** If `build-dashboard-snapshot.ts`
  doesn't support a need, document it in `DASHBOARD-NOTES.md` as a
  limitation. Don't write replacement TS in the skill.
- **Append-only memory.** History snapshots accumulate in Postgres;
  never run a delete or "fix" past data.
- **Cron-friendly.** All inputs gathered up-front; if missing, exit
  with a single error.

## Architecture (for reference)

```
.claude/skills/dashboard-builder/SKILL.md         (this file — orchestration)
scripts/build-dashboard-snapshot.ts               (canonical fetch + aggregate)
scripts/save-dashboard-snapshot.ts                (Postgres insert)
dashboard-app/                                    (Next.js viewer, deployed to Vercel)
└── reads dashboard_snapshots table at view time
└── rolls up daily → user-selected granularity
└── filters by date range / sources / campaigns
```

The script and the dashboard-app share a contract: V2 daily blob shape
defined in `dashboard-app/lib/types.ts` (`funnel_daily`, `sources_daily`,
`campaigns_daily`, plus pre-aggregated `kpis` and `sources` for the
default-view fast path). When that contract changes, both sides update
in lockstep.
