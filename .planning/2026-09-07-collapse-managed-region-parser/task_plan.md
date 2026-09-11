# Task Plan: Collapse Managed Region Parser & Standardize Boundary Formats

## Goal

Collapse `ManagedRegionParser` in `.agents/ageroot_core/comparison.py` into a deep module with a compact public interface (`merge() -> RegionMergeResult`, `has_region_markers() -> bool`), standardizing region boundaries across three explicit types (Type 1: VS Code `#region`, Type 2: metadata `generated-by`, Type 3: skill blocks `<name>-begin`/`<name>-end`), and mirror all changes to `ageroot_template/.agents/ageroot_core/`.

## Next Step

Present verified results to user.

## Current Phase

Phase 5: Verification & Delivery

## Phases

### Phase 1: Exploration & Specification
- [x] Analyze current `ManagedRegionParser` and boundary markers across codebase.
- [x] Complete grilling session standardizing boundary formats into three types.
- [x] Formulate specification in `.scratch/collapse-managed-region-parser/spec.md`.
- **Status:** complete

### Phase 2: Domain Modeling Sync
- [x] Verify alignment with `CONTEXT.md` (`Proposed region merge`, `Malformed region structure`).
- **Status:** complete

### Phase 3: Plan & Delegation Setup
- [x] Create plan in `.planning/2026-09-07-collapse-managed-region-parser/`.
- [x] Set `.planning/.active_plan`.
- **Status:** complete

### Phase 4: Implementation Handoff to Antigravity via Orca
- [x] Create independent worktree `collapse-managed-region-parser` with Antigravity agent via Orca.
- [x] Deliver implementation brief and handoff.
- [x] Antigravity completed implementation and delivered worker report.
- **Status:** complete

### Phase 5: Verification & Delivery
- [x] Review implementation report and diff.
- [x] Run test suite (`PYTHONPATH=.agents python3 -m unittest discover -s .agents/ageroot_core/tests`) - 35/35 pass.
- [x] Verify template mirror synchronization (`ageroot_template/.agents/ageroot_core/`) - 35/35 pass.
- [x] Run regression suite on memory skills (`./tests/run_all.sh` in `ageroot_skills`) - all pass.
- **Status:** complete

## Decisions Made

| Decision | Rationale |
|---|---|
| Deepen Managed Region module | Eliminates leaky untyped segment dicts and error substring parsing; provides clean domain result class. |
| Type 1: VS Code `#region` canonical | Aligns with standard editor folding in VS Code / IDEs. Supports HTML (`<!-- #region -->`), Hash (`# #region`), Slash (`// #region`). `kind:user` default. Anonymous `#endregion` allowed. Legacy `region:` alias retained. |
| Type 2: Metadata directive (`generated-by`) | Standalone file provenance; never wrapped in region tags; normalized by `DeterministicNormalizer`. |
| Type 3: Skill blocks (`<name>-begin` / `<name>-end`) | Strict hyphenated delimiters for now; always default `kind:user` so template updates never overwrite skill rules. |
| Single-call merge seam | `ManagedRegionParser.merge(current, rendered, baseline) -> RegionMergeResult`. Returns `result_class`, `merged_text`, `warnings`, `reason`. |
| Encapsulated marker predicate | `ManagedRegionParser.has_region_markers(text) -> bool`. Eliminates external regex access. |
| Zero external dependencies | Pure Python standard library only. |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| None | 1 | N/A |
