# Worker Report: Consolidate Safety-First Update Engine

**Worker**: Antigravity  
**Date**: 2026-09-06  
**Task**: Consolidate `.agents/ageroot_core/comparison.py` into a deep `AgerootUpdateEngine` module and mirror to `ageroot_template/.agents/ageroot_core/`.

---

## 1. Summary of Changes

Consolidated `.agents/ageroot_core/comparison.py` into a deep, cohesive update engine implementing the architecture defined in Candidate 01 of the architecture review. The module hides configuration loading, baseline snapshot resolution, deterministic normalization, three-way comparison, workspace drift checking, and two-phase transactional commit behind a narrow public interface.

### Public Interface
- `AgerootUpdateEngine(root_dir: Path, config_path: Optional[Path] = None, state_path: Optional[Path] = None)`:
  Initializes update engine, loads `.agents/ageroot.config.yaml` and `.agents/ageroot.state.yaml`, and manages snapshot persistence state.
- `dry_run(renders: dict[str, str], options: Optional[DryRunOptions] = None) -> DryRunReport`:
  Executes pre-apply safety-first comparison, resolves strategy per path, validates external links, checks deletion gating, records pre-apply workspace file hashes, and computes apply eligibility.
- `apply(report: DryRunReport, options: Optional[ApplyOptions] = None) -> ApplyOutcome`:
  Executes atomic apply across workspace files and snapshots. Validates eligibility, verifies pre-apply workspace drift, stages changes to `.agents/.staging-<timestamp>`, verifies SHA-256 integrity, commits moves atomically with backup rollback, and commits state updates atomically.
- `format_summary(report: DryRunReport) -> str`:
  Formats a tiered summary-first confirmation report following ADR-0001 with overview counts and an attention-required section detailing reasons, apply eligibility, warnings, and full diff access.

### Behind the Seam Capabilities
1. **Standard Library YAML Parser/Serializer (`SimpleYamlHelper`)**:
   - Pure Python stdlib parser and dumper with zero third-party dependencies (no PyYAML).
   - Handles scalars (strings, ints, booleans, null), nested dictionaries, lists of dictionaries, and inline collections (`[]`, `{}`).
   - Verified 100% roundtrip fidelity against existing `.agents/ageroot.config.yaml` and `.agents/ageroot.state.yaml`.
2. **Strategy Resolution**:
   - Existing paths in `.agents/ageroot.state.yaml` retain their recorded strategy (`generated`, `managed-regions`, `external-link`).
   - New paths are inspected for region markers (`<!-- region:` or legacy `<!-- *-begin`); if present, resolved to `managed-regions`; otherwise resolved to `generated`.
3. **State-Driven External Link Validation**:
   - Paths with `strategy: external-link` in state are validated for link existence and target resolution.
   - External links absent from `renders` are never treated as deletions.
4. **Pre-Apply Workspace Drift Check**:
   - `dry_run` records SHA-256 hashes of all observed workspace files.
   - `apply` verifies that no files were modified, created, or deleted between dry run and apply. Any drift immediately aborts the operation without touching files.
5. **Staged Two-Phase Transactional Snapshot Commit**:
   - Phase 1: Stages all modified/created files, snapshots, and updated state into `.agents/.staging-<timestamp>/`. Verifies all SHA-256 hashes against expectations.
   - Phase 2: Performs atomic replacement (`Path.replace`) for workspace files, snapshots, and state file. If any error occurs during atomic moves, original files are restored from backup.
   - Staging directories are guaranteed to be cleaned up on both success and failure.
6. **Deletion Escalation & Gating**:
   - Managed files absent from renders require explicit `allow_deletions=True` to be eligible for apply (`DELETION_PENDING`).
   - Locally modified deletions are strictly `BLOCKED` and cannot be applied even with `allow_deletions=True`.
7. **Planning Isolation**:
   - Paths under `.planning/` are excluded from comparison, reporting, and applying, preserving the boundary with the `planning-with-files` skill.

---

## 2. Test Suite & Test Surface

The interface is the test surface. `.agents/ageroot_core/tests/test_comparison.py` was rewritten to test primarily through `engine.dry_run()` and `engine.apply()` against simulated workspace environments, while preserving low-level unit tests for `DeterministicNormalizer`, `ManagedRegionParser`, and `SnapshotStore`.

### Test Cases (24 Tests)
1. `TestDeterministicNormalizer.test_crlf_and_trailing_whitespace`
2. `TestDeterministicNormalizer.test_empty_string`
3. `TestDeterministicNormalizer.test_generated_by_provenance_is_metadata_only`
4. `TestSnapshotStore.test_write_and_read_snapshot_with_integrity`
5. `TestManagedRegionParser.test_valid_region_parsing`
6. `TestManagedRegionParser.test_malformed_region_unpaired`
7. `TestManagedRegionParser.test_malformed_region_nested`
8. `TestManagedRegionParser.test_region_merge_preserves_user_and_updates_generated`
9. `TestManagedRegionParser.test_concurrent_edit_in_generated_region_is_conflict`
10. `TestSimpleYamlHelper.test_yaml_parse_and_dump_roundtrip`
11. `TestAgerootUpdateEngine.test_clean_generated_dry_run_and_apply`
12. `TestAgerootUpdateEngine.test_planning_path_excluded_from_dry_run_and_reporting`
13. `TestAgerootUpdateEngine.test_strategy_autodetection_for_new_paths`
14. `TestAgerootUpdateEngine.test_managed_regions_merge_and_conflict`
15. `TestAgerootUpdateEngine.test_workspace_drift_detection_modified`
16. `TestAgerootUpdateEngine.test_workspace_drift_detection_created`
17. `TestAgerootUpdateEngine.test_workspace_drift_detection_deleted`
18. `TestAgerootUpdateEngine.test_snapshots_disabled_policy`
19. `TestAgerootUpdateEngine.test_snapshot_corruption_and_one_time_override`
20. `TestAgerootUpdateEngine.test_external_link_validation_and_persistence`
21. `TestAgerootUpdateEngine.test_deletion_escalation_clean_and_modified`
22. `TestAgerootUpdateEngine.test_staging_cleanup_and_transactional_rollback`
23. `TestAgerootUpdateEngine.test_transactional_rollback_on_apply_failure`
24. `TestAgerootUpdateEngine.test_format_summary_tiered_reporting`

### Test Verification
Ran against `.agents/ageroot_core/`:
```
........................
----------------------------------------------------------------------
Ran 24 tests in 0.044s

OK
```

Ran against `ageroot_template/.agents/ageroot_core/`:
```
........................
----------------------------------------------------------------------
Ran 24 tests in 0.045s

OK
```

---

## 3. Template Mirror Synchronization

All changes were mirrored to `ageroot_template/.agents/ageroot_core/`:
- `ageroot_template/.agents/ageroot_core/__init__.py`
- `ageroot_template/.agents/ageroot_core/comparison.py`
- `ageroot_template/.agents/ageroot_core/tests/test_comparison.py`

Both codebases are in complete synchronization.
