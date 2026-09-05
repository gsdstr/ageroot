# AGENTS.md — Adapter for Ageroot

Reads `AGENTS.md` before doing any work. This file points it at
the portable brain in `.agents/`.

## Startup
Read `.agents/AGENTS.md` before doing any work.

## Hard rules
- No force push to `main`, `production`, `staging`.

## Managed `.agents/AGENTS.md`

`.agents/AGENTS.md` uses `managed-regions`. Keep its markers intact and add
project-specific instructions only in its `project` user region.

## Agent skills

### Issue tracker

Issues are tracked as local markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses default canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

Uses a single-context layout. See `docs/agents/domain.md`.
