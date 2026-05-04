---
name: memory-update
description: >
  Update client memory after a work session. Overwrites clients/state/<id>.md
  with the new current snapshot and appends a dated entry to clients/logs/<id>.md
  with session summary, decisions, findings, and next steps. Single entry point
  for writing to memory — never edit these files by hand. Activate when user
  says "update memory", "log this session", "save state", "remember this",
  "update LeadGenCo state", or at the end of any significant work session.
---

# Memory Update — Client State + Log Maintenance

Three-file memory model: `briefs/` (static), `state/` (current snapshot,
overwritten), `logs/` (append-only history). This skill writes to `state/`
and `logs/`. Never touches `briefs/`.

## Required Inputs

- `client_id` (required)
- `session_summary` (optional) — if omitted, infer from conversation context
  since last memory update
- `session_type` (optional) — one of: `audit`, `diagnostic`, `copy`,
  `strategy`, `config`, `bug fix`, `infra`, `other`. Default inferred from
  session content.

Fail fast if `client_id` missing.

## Process

### 1. Read existing memory

Before writing anything, load:
- `clients/briefs/<client_id>.md` — static context (read-only, don't modify)
- `clients/state/<client_id>.md` — current state (will be overwritten)
- `clients/logs/<client_id>.md` — history (entries will be prepended to)

If state/ or log/ missing, treat as first-time write.

### 2. Ingest latest reports

Check `./reports/<client_id>/` directory for any report directories modified
since the last log entry timestamp. For each:

- Read the main `.md` report (look for the `SCORE:` header line)
- Capture: skill name, run date, SCORE/GRADE, top 3 critical findings,
  top 3 recommendations
- Extract any config facts surfaced (pipeline IDs, QS distribution,
  wasted spend estimate, cohort counts, etc.)

Report findings feed `Recent Audit Scores`, `Tracking / Config State`,
and the log entry. Never include raw report text in state — only the
distilled facts.

If no new reports → skip this step, note in session summary.

### 3. Diff state from session + reports

Extract from conversation context since last log entry **and** from
newly-ingested reports:

- **Marketing Strategy** — positioning changes, new angles discussed,
  ICP refinements, quarterly priorities set. This is the "what are we
  trying to do for this client" snapshot.
- **Live Campaigns** — new campaigns launched, paused, renamed; budget
  changes; bid-strategy changes; objective shifts. Ideally a table:
  platform × campaign name × daily budget × status × bid strategy.
- **Active Experiments** — A/B tests started or ended; hypothesis +
  expected outcome + current result.
- **Current Blockers** — things blocking progress until resolved
  (tracking bug, awaiting access, API downtime, client review needed).
- **Pending Decisions** — awaiting client input, awaiting data.
- **Recent Audit Scores** — any audit skill ran this session or
  surfaced from reports ingest. Score + grade + report path + run date.
- **Tracking / Config State** — config values resolved (pipeline IDs,
  property names, customer IDs, conversion action names, etc.).
- **Open Questions** — surfaced but unanswered.

Carry forward anything from existing state that hasn't changed. Remove
items that are resolved (blockers fixed, decisions made, questions
answered).

### 4. Write new state

Overwrite `clients/state/<client_id>.md` with frontmatter:

```markdown
---
client_id: <id>
updated: <YYYY-MM-DD>
---

## Marketing Strategy
## Live Campaigns
## Active Experiments
## Current Blockers
## Pending Decisions
## Recent Audit Scores
## Tracking / Config State
## Open Questions
```

Missing sections → omit (don't leave empty H2s).

### 5. Append log entry

Prepend to `clients/logs/<client_id>.md` (newest-first — always add at top,
not bottom):

```markdown
## <YYYY-MM-DD> — <short title>
**Session type:** <type>

- bullet 1 (what happened)
- bullet 2
- bullet 3

**Decisions:** <comma-separated list, or "none">
**Findings:** <comma-separated list, or "none">
**Next:** <short sentence or "none">

---

<previous entries here, unchanged>
```

Short title: 5–8 words max. Bullets: past tense, specific facts not vibes.

### 6. Emit summary

Return to caller a one-block summary:

- state file: overwritten or newly created
- log file: number of lines prepended
- next-action list extracted from log

## Hard Rules

- **Never edit past log entries.** Logs are append-only. Historical accuracy
  matters more than retroactive cleanup.
- **Never touch `briefs/`.** Sector / ICP / compliance facts are the user's
  domain. If something in the brief looks wrong, flag it in the log under
  `Findings:` — don't self-edit.
- **Don't invent state.** If the session didn't produce info for a section,
  omit the section (or keep the prior value). Never guess "probably active
  campaigns" or similar.
- **Dates are ISO (`YYYY-MM-DD`).** Always.
- **When called without client_id**, refuse — cross-client state bleed is
  the failure mode this skill exists to prevent.
- **If multiple clients touched in one session**, run the skill once per
  client. Don't batch.

## When NOT to use

- Mid-session — skill should run at the end of meaningful work, not between
  each tool call. Mid-session updates create noise in the log.
- On read-only sessions where nothing changed (e.g. user asked a question,
  got an answer, moved on — no need to log).
- On trivial sessions (< 5 exchanges, no decisions, no findings).

## Output

No report file. Just updates `clients/state/<client_id>.md` +
`clients/logs/<client_id>.md` and returns a short confirmation block:

```
Memory updated for <client_id>.
  state/ overwritten  — <N> sections
  logs/  prepended    — <N> lines, session type: <type>
  Next actions logged: <count>
```
