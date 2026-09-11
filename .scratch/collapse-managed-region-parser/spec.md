# Collapse Managed Region Parser and Merge Engine

Status: ready-for-agent

## Problem Statement

Files containing managed regions and template metadata require deterministic inspection, validation, and three-way merge logic to safely distinguish user-owned content from generated template updates. Currently, this capability exhibits several architectural friction points:

1. **Shallow and Leaky Parser Interface**: The managed region parser forces callers to coordinate a two-step sequence: raw structural parsing into untyped dictionaries with loose string keys, followed by merge orchestration.
2. **Error String Discrimination**: The merge routine returns untyped string tuples and generic error messages. Callers (such as the update engine) are forced to inspect error text using substring matching (e.g. checking whether an error contains `"Concurrent edit"`) to deduce whether a failure represents a concurrent modification conflict or a malformed region structure.
3. **Unstandardized Region Syntax**: Region boundary markers are currently scattered across ad-hoc patterns: legacy hyphenated shorthands, colon-delimited directives, and standalone metadata markers.
4. **Lack of Editor Alignment**: The current syntax does not natively align with industry-standard VS Code and IDE folding conventions (`#region` / `#endregion`), preventing developers from using native editor folding in managed configuration files.
5. **Ambiguous Ownership Rules**: Shorthand skill blocks (such as `caveman` or `rtk`) currently rely on hardcoded name lookups in parser code to guess whether content is generated or user-owned, rather than following an explicit, standardized taxonomy.

## Solution

Standardize region and metadata boundaries into three explicit types, and collapse the region parsing, validation, marker detection, and merge mechanics into a single deep module behind a compact domain interface:

1. **Three Standardized Boundary Types**:
   - **Type 1: VS Code `#region` (Canonical Primary Syntax)**: Standard across code and markdown files. Supports HTML comments (`<!-- #region name -->`), hash comments (`# #region name`), and slash comments (`// #region name`). Supports explicit `kind:user` or `kind:generated` (defaulting to `user`). Supports both anonymous closing (`#endregion` popping LIFO stack) and named closing (`#endregion name` with strict name matching). Legacy `region:name` syntax is retained as a backwards-compatible alias.
   - **Type 2: Metadata Directive (`generated-by`)**: Unwrapped, single-line file-level provenance directive (e.g., `<!-- generated-by: ageroot ... -->` or `# generated-by: ageroot ...`). Never wrapped in `#region` or `-begin`/`-end` blocks. Handled as unmanaged metadata and deterministically normalized to eliminate diff churn.
   - **Type 3: Skill-Owned Blocks (`<name>-begin` / `<name>-end`)**: Dedicated blocks owned by auxiliary agent skills (such as `caveman` or `rtk`). Formatted strictly as `<name>-begin` and `<name>-end`. Always classified as `user`-owned by default, ensuring Ageroot template updates preserve skill instructions verbatim without overwriting them.
2. **One-Call Deep Merge Interface**: Replace the multi-step parsing and tuple-returning interface with a unified merge method: `merge(current_text, new_rendered_text, baseline_text=None) -> RegionMergeResult`.
3. **Direct Domain Outcomes**: Return strongly typed domain classifications directly (`ResultClass.REGION_MERGE`, `ResultClass.CONFLICT`, `ResultClass.BLOCKED`, `ResultClass.UNCHANGED`) alongside merged text, warnings, and structured diagnostic reasons, completely eliminating error string parsing.
4. **Encapsulated Marker Detection**: Expose a clean predicate method (`has_region_markers(text) -> bool`) so callers never touch private regular expressions.

## User Stories

1. As an update engine, I want to execute a region merge via a single method call with current, rendered, and baseline texts, so that I do not need to orchestrate parsing, AST inspection, or segment reconstruction manually.
2. As an update engine, I want to receive a strongly typed domain result class directly from the merge operation, so that I never have to perform substring checks on error text to distinguish conflicts from structural blocks.
3. As an update engine, I want to check whether arbitrary text contains declared region boundaries via a clean boolean method, so that I do not need to access or match against private regular expressions.
4. As a developer using VS Code or JetBrains, I want Ageroot managed regions formatted as `<!-- #region name -->` and `<!-- #endregion -->`, so that I can fold and unfold managed blocks natively in my editor.
5. As a developer editing files with hash comments (like YAML, Python, or shell scripts), I want `#region` markers formatted with `# #region name`, so that region boundaries respect the target language's syntax.
6. As a developer editing files with slash comments (like TypeScript, JavaScript, or Go), I want `#region` markers formatted with `// #region name`, so that region boundaries are valid comments in those languages.
7. As a developer, I want anonymous `<!-- #endregion -->` closing tags to be supported, so that I do not have to repeat long region names on closing tags.
8. As a developer who writes named closing tags (`<!-- #endregion name -->`), I want the parser to strictly verify that the closing name matches the opening tag, so that typos and structural misalignments are caught immediately.
9. As a developer, I want `#region` blocks without an explicit `kind` attribute to default to `kind:user`, so that custom sections I author are safely preserved by default.
10. As a template author, I want to specify `kind:generated` on `#region` blocks, so that the update engine knows to update those sections when templates change.
11. As a project maintainer, I want existing files using `<!-- region:name kind:... -->` and `<!-- endregion:name -->` to continue merging correctly without migration churn, so that existing installations remain fully supported.
12. As an agent reading project instructions, I want `<!-- generated-by: ageroot ... -->` provenance comments to be treated as standalone metadata, so that file-level provenance does not require synthetic region boundaries.
13. As an update engine, I want `generated-by` metadata differences to be deterministically normalized, so that timestamp, version, or commit differences alone never trigger an update or a merge conflict.
14. As an auxiliary agent skill (such as `caveman` or `rtk`), I want my instructions enclosed in `<!-- <name>-begin -->` and `<!-- <name>-end -->`, so that my prompt rules have clear, identifiable delimiters.
15. As an auxiliary agent skill author, I want skill-owned blocks to be treated as user-owned by default, so that template updates do not overwrite skill-specific configuration.
16. As a developer, I want accidental structural errors (unclosed regions or unmatched end tags) to produce a `BLOCKED` outcome with descriptive diagnostic text, so that corrupted files prevent unsafe updates.
17. As a developer, I want nested region declarations to be rejected as `BLOCKED`, so that ambiguous hierarchical region structures are forbidden.
18. As a developer modifying generated regions locally, I want concurrent modifications to produce a `CONFLICT` outcome, so that upstream changes do not silently overwrite my local edits.
19. As a developer modifying user regions, I want the merge operation to emit a warning while preserving my changes, so that I have clear visibility that local customizations were retained.
20. As an update engine, I want merged outputs that are identical to current workspace content to be classified as `UNCHANGED`, so that redundant file writes are skipped.
21. As an update engine, I want newly added regions in an upstream template to be smoothly inserted into the merged output, so that new template features appear in the updated file.
22. As an update engine, I want empty user regions to be preserved without stripping, so that intentionally blank user sections remain intact.
23. As a test author, I want to test region merge behavior through one unified interface, so that test fixtures do not break when internal segment representations change.
24. As a maintainer, I want all tokenizing, marker parsing, and merge state hidden behind the module seam, so that internal parsing optimizations do not leak into caller code.

## Implementation Decisions

1. **Consolidated Module Boundary**:
   The existing separate parsing helper and merge routines are collapsed into a cohesive module. The public interface is narrowed to two entry points:
   - `merge(current_text: str, new_rendered_text: str, baseline_text: Optional[str] = None) -> RegionMergeResult`
   - `has_region_markers(text: str) -> bool`

2. **Standardized Boundary Syntax Taxonomy**:
   The module recognizes three distinct boundary classes:
   - **Type 1: `#region` Directives**:
     Opening pattern matches across comment styles (`<!--`, `#`, `//`):
     `(?P<comment_start><!--|#|//)\s*#region\s+(?P<name>[\w-]+)(?:\s+kind:(?P<kind>user|generated))?\s*(?P<comment_end>-->)?`
     Closing pattern matches:
     `(?P<comment_start><!--|#|//)\s*#endregion(?:\s+(?P<name>[\w-]+))?\s*(?P<comment_end>-->)?`
     Backwards compatibility: Legacy `region:(?P<name>[\w-]+)` and `endregion:(?P<name>[\w-]+)` are accepted as aliases for Type 1.
   - **Type 2: Metadata Directives**:
     Single-line unwrapped directives matching:
     `(?P<comment_start><!--|#|//)\s*generated-by:\s*ageroot(?:;.*?)?\s*(?P<comment_end>-->)?`
     Treated as unmanaged content; normalized by deterministic normalization rules.
   - **Type 3: Skill Blocks**:
     Hyphenated shorthand pairs matching:
     `(?P<comment_start><!--|#|//)\s*(?P<name>[\w-]+)-begin\s*(?P<comment_end>-->)?`
     `(?P<comment_start><!--|#|//)\s*(?P<name>[\w-]+)-end\s*(?P<comment_end>-->)?`
     Strict `-begin` and `-end` syntax. Ownership defaults strictly to `kind:user`.

3. **Typed Merge Result Shape**:
   The merge method returns a typed result object rather than a tuple of booleans and strings.
   *Prototype Shape*:
   ```python
   @dataclass
   class RegionMergeResult:
       result_class: ResultClass
       merged_text: Optional[str]
       warnings: List[str] = field(default_factory=list)
       reason: Optional[str] = None
       diff: Optional[str] = None
   ```
   *(Encapsulates domain outcome directly; eliminates caller-side string inspection).*

4. **Stack Resolution & Anonymity Semantics**:
   - When encountering an opening marker, push the marker record onto the region stack.
   - When encountering a closing marker:
     - If the stack is empty, fail with `ResultClass.BLOCKED` (unmatched closing tag).
     - If closing marker is anonymous (`#endregion`), pop the topmost region from the stack.
     - If closing marker is named (`#endregion name` or `<name>-end`), pop the topmost region and verify names match. A mismatch fails with `ResultClass.BLOCKED`.
   - If the stack is not empty at end-of-file, fail with `ResultClass.BLOCKED` (unclosed region).
   - If an opening marker is encountered while the stack is non-empty, fail with `ResultClass.BLOCKED` (nested regions disallowed).

5. **Ownership Defaults & Merge Semantics**:
   - Type 1 (`#region`): `kind:generated` updates from template; `kind:user` (or omitted kind) preserves current workspace content.
   - Type 3 (Skill blocks): Always `kind:user`. Preserves current workspace content; template updates do not overwrite skill instructions.
   - Concurrent modification: If a `kind:generated` region was modified locally relative to baseline while template also changed, return `ResultClass.CONFLICT`.
   - Local edit preservation: If a `kind:user` region differs from baseline, emit a preservation warning and return `ResultClass.REGION_MERGE`.
   - Identity check: If the merged text matches current workspace text, return `ResultClass.UNCHANGED`.

6. **Elimination of Untyped Dictionaries**:
   All internal segment representations transition from loose string-keyed dictionaries to lightweight typed internal classes, completely hidden behind the module interface.

7. **Integration with the Update Engine**:
   The core comparison engine and update engine invoke `merge` directly and inspect `RegionMergeResult.result_class`, deleting all caller-side regex matching and error message parsing.

## Testing Decisions

1. **Test Philosophy (The Interface is the Test Surface)**:
   Tests evaluate only external behavior across the public interface. Tests provide input strings (current, rendered, baseline) and assert properties on `RegionMergeResult` (`result_class`, `merged_text`, `warnings`, `reason`). Tests do not invoke internal tokenizers or inspect private segment stacks.

2. **Test Coverage Matrix**:
   - **Type 1 Tests**:
     - `<!-- #region name kind:generated -->` clean update (`REGION_MERGE`).
     - `<!-- #region name kind:user -->` local preservation with warning (`REGION_MERGE`).
     - Anonymous `<!-- #endregion -->` closing tag resolution.
     - Named `<!-- #endregion name -->` matching and mismatch rejection (`BLOCKED`).
     - `# #region name` and `// #region name` multi-comment prefix support.
     - Legacy `<!-- region:name kind:... -->` backwards compatibility.
   - **Type 2 Tests**:
     - `<!-- generated-by ... -->` metadata normalization and diff-free behavior.
   - **Type 3 Tests**:
     - `<!-- caveman-begin -->` / `<!-- caveman-end -->` user ownership preservation.
     - `<!-- rtk-begin -->` / `<!-- rtk-end -->` user ownership preservation.
     - Custom `<name>-begin` / `<name>-end` user ownership preservation.
   - **Structural Error Tests**:
     - Unclosed opening marker (`BLOCKED`).
     - Unmatched closing tag (`BLOCKED`).
     - Mismatched closing tag (`BLOCKED`).
     - Nested regions (`BLOCKED`).
   - **Conflict Tests**:
     - Concurrent edit in `kind:generated` region (`CONFLICT`).
   - **Predicate Tests**:
     - `has_region_markers()` returns `True` for Type 1 and Type 3, `False` for plain text or Type 2 standalone metadata.

3. **System Integration Seam**:
   Existing update engine tests in `test_comparison.py` continue to verify end-to-end dry-run reporting, apply gating, and tiered summary generation for files containing managed regions.

## Out of Scope

- Cross-file region references or shared transcluded regions.
- Interactive conflict resolution or GUI region editors.
- Support for nested region hierarchies.
- Changes to the deterministic text normalization algorithms beyond standardizing metadata comments.

## Further Notes

- Aligns strictly with domain definitions in `CONTEXT.md` for `Proposed region merge` and `Malformed region structure`.
- Preserves the drop-in requirement of using Python standard library features only with zero external dependencies.
- Retains compatibility with `ADR-0001` (Summary-first confirmation) by providing clean result classes and reasons for tiered reporting.
