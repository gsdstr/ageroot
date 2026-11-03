# Task Plan: Monorepo Unification and Distribution Module

## Goal
Unify `ageroot_template` and `ageroot_skills` into `ageroot` monorepo. Build and verify Distribution module (`ageroot_core.distribution`) with component manifest, automated directory expansion, whole-payload check, and clean consumer lifecycle.

## Next Step
Deliver final summary and reviewable diff to Owner.

## Current Phase
Phase 5: Delivery (complete)

## Phases

### Phase 1: Source Migration & Provenance
- [x] Create `docs/PROVENANCE.md` capturing `ageroot_template` (`1fb3c55`) and `ageroot_skills` (`2508bdc`) commit hashes and remotes.
- [x] Copy canonical engine to `packages/ageroot_core/`.
- [x] Copy canonical skills to `skills/` (`memory-manager`, `memory-maintenance`).
- [x] Copy templates and configuration (`templates/`, root `package.json`, `scripts/sync-plugin-version.mjs`).
- [x] Verify non-destructive copy, stage and commit Step 1 (`220734b`).
- [x] Remove `ageroot_template/` and `ageroot_skills/`, remove them from `.gitignore`, commit Step 2 (`9a63a43`).
- **Status:** complete

### Phase 2: Distribution Module Implementation
- [x] Create `packages/ageroot_core/distribution/` (`manifest.py`, `collector.py`, `service.py`, `__main__.py`).
- [x] Implement declarative manifest with components: `core`, `orchestration`, `orca_adapter`, `memory`.
- [x] Implement automatic directory expansion into file paths for `renders` and `managed_files`.
- [x] Implement CLI: `--check`, `--export <dir>`, `--sync-local`.
- [x] Update `scripts/sync-orchestration-package.py` to support `orca_adapter` overlay without drift error.
- **Status:** complete

### Phase 3: Test Suite & Tooling Consolidation
- [x] Consolidate tests into `tests/` or unified runner `scripts/test.sh`.
- [x] Add unit tests for Distribution module (`test_distribution.py`).
- [x] Verify 35 existing comparison tests continue to pass (now 39 total).
- [x] Run memory skills tests (`sh skills/tests/run_all.sh` - all 5 suites PASS).
- **Status:** complete

### Phase 4: Consumer Lifecycle & End-to-End Verification
- [x] Run `--check` against canonical source; verify Orca adapter does not cause false drift.
- [x] Test clean export to disposable consumer directory.
- [x] Verify dry-run and atomic apply in disposable consumer with snapshot baselines.
- [x] Verify `--sync-local` against consumer preserving user regions in `AGENTS.md` and `.agents/AGENTS.md`.
- **Status:** complete

### Phase 5: Documentation & Return Contract
- [x] Update `README.md` and `templates/core/.agents/SETUP.md` with new monorepo layout and distribution CLI.
- [x] Prepare final reviewable diff and summary.
- **Status:** complete

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| ADR-0003 Monorepo unification | Single source of truth for authoring; clear separation from consumer dogfood. |
| Flat provenance import | Clean commit graph with exact upstream provenance metadata in `docs/PROVENANCE.md`. |
| Component-based distribution | Minimal default payload (`core` + `orchestration`); `memory` is opt-in component. |
| Automatic directory expansion | Eliminates directory entries in `state.yaml` and false deletion proposals. |
| Baseline snapshots on export | Ensures consumer can run atomic dry-run/apply without unverified bootstrap error. |

## Errors Encountered
| Error | Resolution |
|-------|------------|
| Missing snapshots on export | Updated `export_payload` to write initial baseline snapshots in `.agents/snapshots/` and record hashes in `state.yaml`. |
| Default `--target` in CLI | Changed default target from `None` to `Path(".")` so running in consumer directory updates consumer instead of source. |
