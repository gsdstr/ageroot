# Task Plan: Consolidate Safety-First Update Engine

## Goal

Consolidate `.agents/ageroot_core/comparison.py` into a deep `AgerootUpdateEngine` module exposing a small public interface (`dry_run`, `apply`, `format_summary`) and hiding state loading, baseline reading, deterministic normalization, three-way comparison, workspace drift checks, and staged two-phase transactional snapshot commit.

## Next Step

Present verified implementation results to user.

## Current Phase

Phase 5: Verification & Delivery

## Phases

### Phase 1: Architecture Review & Grilling Loop
- [x] Walk commit history and identify architectural hot spots.
- [x] Generate HTML architecture review report with 4 candidates.
- [x] Present report and obtain user selection (Candidate 01).
- [x] Complete 3-round grilling decision tree on constraints, seam, failure recovery, and test surface.
- **Status:** complete

### Phase 2: Domain Modeling Sync
- [x] Update `CONTEXT.md` with definitions for `Update engine` and `Workspace drift check`.
- **Status:** complete

### Phase 3: Planning & Specification
- [x] Formulate complete implementation specification and acceptance criteria.
- [x] Initialize isolated `.planning/2026-09-06-consolidate-update-engine/` plan.
- [x] Update `.planning/.active_plan`.
- **Status:** complete

### Phase 4: Implementation Handoff to Antigravity via Orca
- [x] Create independent worktree `consolidate-update-engine` with Antigravity agent via Orca.
- [x] Deliver complete implementation brief and handoff.
- [x] Antigravity completed implementation and delivered worker report.
- **Status:** complete

### Phase 5: Verification & Delivery
- [x] Review implementation report and diff.
- [x] Run test suite (`PYTHONPATH=.agents python3 -m unittest discover -s .agents/ageroot_core/tests`) - 24/24 pass.
- [x] Verify template mirror synchronization (`ageroot_template/.agents/ageroot_core/`) - 24/24 pass.
- [x] Run regression suite on memory skills (`./tests/run_all.sh` in `ageroot_skills`) - all pass.
- **Status:** complete

## Decisions Made

| Decision | Rationale |
|---|---|
| Deepen Update Engine (Candidate 01) | Update safety and atomic commit are core responsibilities of Ageroot; currently fragmented across callers. |
| In-memory render input (`dict[str, str]`) | Decouples template rendering mechanism from safety comparison and atomic commit at a clean seam. |
| Staged two-phase commit (`.agents/.staging-<timestamp>`) | Enforces all-or-nothing atomic apply and transactional snapshot commit; zero workspace mutation on failure. |
| Seam surface: `dry_run` and `apply` public | Shrinks interface; `compare_path` becomes private implementation detail. Interface is the test surface. |
| Strategy resolution | State-governed for existing paths; auto-detect `managed-regions` for new paths; default `generated`. |
| Workspace drift check | Pre-apply check verifying workspace file hashes match dry-run inspection to prevent concurrent edit overwrites. |
| External links | State-driven validation; external links never treated as deleted just because absent from `renders`. |
| Domain additions | Defined `Update engine` and `Workspace drift check` in `CONTEXT.md`. |
| Package structure | Keep in `.agents/ageroot_core/comparison.py` and export `AgerootUpdateEngine`, `DryRunReport`, `ApplyOutcome` from `__init__.py`. Mirror to `ageroot_template`. |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| None | 1 | N/A |
