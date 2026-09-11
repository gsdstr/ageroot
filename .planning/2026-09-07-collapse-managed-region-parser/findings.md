# Findings & Architecture Decisions: Managed Region Consolidation

## Core Problem
- `ManagedRegionParser` currently exposes `parse_structure` returning untyped `List[dict]`, and `merge` returning a 4-item tuple `Tuple[bool, Optional[str], List[str], Optional[str]]`.
- Callers must inspect error strings (`if "Concurrent edit" in (merge_err or "")`) to deduce `ResultClass.CONFLICT` vs `ResultClass.BLOCKED`.
- Callers inspect `ManagedRegionParser.MARKER_PATTERN` directly via regex rather than calling a method.
- Markers are unstandardized and do not support VS Code `#region` folding or multi-language comments.

## Target Architecture
- **Public Interface**:
  - `ManagedRegionParser.merge(current_text: str, new_rendered_text: str, baseline_text: Optional[str] = None) -> RegionMergeResult`
  - `ManagedRegionParser.has_region_markers(text: str) -> bool`
- **Data Shape**:
  ```python
  @dataclass
  class RegionMergeResult:
      result_class: ResultClass
      merged_text: Optional[str]
      warnings: List[str] = field(default_factory=list)
      reason: Optional[str] = None
      diff: Optional[str] = None
  ```
- **Standardized Boundary Syntax**:
  - **Type 1: VS Code `#region` (Canonical)**:
    - `<!-- #region <name> [kind:<user|generated>] -->` ... `<!-- #endregion [<name>] -->`
    - `# #region <name> [kind:<user|generated>]` ... `# #endregion [<name>]`
    - `// #region <name> [kind:<user|generated>]` ... `// #endregion [<name>]`
    - Anonymous `#endregion` pops LIFO stack. Named `#endregion <name>` strictly verifies match.
    - Legacy alias: `<!-- region:<name> ... -->` / `<!-- endregion:<name> -->`.
    - Ownership defaults to `kind:user` if unspecified; `kind:generated` if explicitly declared.
  - **Type 2: Metadata directive (`generated-by`)**:
    - Standalone single-line directive. Treated as unmanaged content; masked/normalized by `DeterministicNormalizer`.
  - **Type 3: Skill blocks (`<name>-begin` / `<name>-end`)**:
    - `<!-- <name>-begin -->` ... `<!-- <name>-end -->` (and `# <name>-begin` / `# <name>-end`).
    - Always `kind:user` (preserved across updates; skills manage their own content).
    - Disallows nesting.
- **Update Engine Integration**:
  - `ThreeWayComparisonEngine.compare_path` calls `ManagedRegionParser.merge(...)` and uses `result.result_class` directly without error string matching.
  - `AgerootUpdateEngine.dry_run` calls `ManagedRegionParser.has_region_markers(content)` instead of searching `MARKER_PATTERN`.
- **Test Surface**:
  - All tests in `test_comparison.py` test across `merge()` and `has_region_markers()`.
- **Sync**:
  - Mirror all changes and tests to `ageroot_template/.agents/ageroot_core/`.
