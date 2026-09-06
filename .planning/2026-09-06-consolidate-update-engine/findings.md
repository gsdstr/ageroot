# Findings & Architecture Decisions

## Core Problem
- `ThreeWayComparisonEngine` in `.agents/ageroot_core/comparison.py` only implements single-file comparison via `compare_path(...)`.
- Callers must manually load `ageroot.config.yaml` and `ageroot.state.yaml`, iterate over files, handle missing files, and invoke `SummaryReport.format_summary`.
- Atomic apply and transactional snapshot commit are completely unexpressed in the module; `SnapshotStore.write_snapshot_atomic` only writes one snapshot file at a time directly to disk with no rollback.

## Architecture Target: AgerootUpdateEngine
- **Public Interface**:
  - `AgerootUpdateEngine(root_dir: Path, config_path: Path | None = None, state_path: Path | None = None)`
  - `dry_run(renders: dict[str, str], options: DryRunOptions | None = None) -> DryRunReport`
  - `apply(report: DryRunReport, options: ApplyOptions | None = None) -> ApplyOutcome`
  - `format_summary(report: DryRunReport) -> str`
- **Behind the Seam**:
  - Encapsulates config parsing (`snapshots: enabled|disabled`).
  - Encapsulates state parsing (`schema`, `template`, `managed_files`).
  - Strategy assignment: state strategy for known paths; auto-detect `<!-- region:` or legacy `<!-- *-begin` in content for new paths; default `generated`.
  - State-driven `external-link` validation: verifies target existence and symlink resolution without treating absence from `renders` as deletion.
  - Deletion detection: paths in state (renderer-owned) missing from `renders` become `deletion-pending` (or `blocked` if locally modified vs baseline).
  - Normalization: deterministic formatter-only whitespace and provenance normalization.
  - Workspace drift check: records SHA-256 of workspace files during dry run; verifies hashes before mutating files in `apply()`.
  - Staged two-phase transactional commit:
    1. Pre-apply check: `report.is_eligible` is True, workspace files have not drifted.
    2. Stage all updated files and new baseline snapshots in `.agents/.staging-<timestamp>/`.
    3. Verify all SHA-256 hashes match.
    4. Atomically move staged files to workspace and staged snapshots to `.agents/snapshots/`.
    5. Write updated `.agents/ageroot.state.yaml` with new timestamps, snapshots, and SHA-256 hashes.
    6. If any step fails, remove staging directory and abort without corrupting workspace.
- **Test Surface**:
  - Rewrite test suite in `.agents/ageroot_core/tests/test_comparison.py` to exercise `dry_run` and `apply` against simulated workspace directories.
  - Keep low-level unit tests for `DeterministicNormalizer` and `ManagedRegionParser`.
- **Sync**:
  - Mirror code and tests to `ageroot_template/.agents/ageroot_core/`.
