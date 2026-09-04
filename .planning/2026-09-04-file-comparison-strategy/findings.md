# Findings & Decisions

## Requirements

- Design the strategy for comparing files described by `.agents/SETUP.md`.
- Keep update application behind an explicit user confirmation.

## Research Findings

- `.agents/ageroot.state.yaml` is authoritative for managed paths and their render strategies.
- Managed strategies currently used: `generated`, `external-link`; SETUP also documents `managed-regions`.
- Existing architecture states that `PREFERENCES.md` is user-editable but still participates in dry-run comparison.
- Existing open question: improve the file-comparison protocol.
- User selected a safety-first dry-run comparison contract.
- User selected a hybrid baseline: three-way for `generated` and `managed-regions`; two-way for `external-link`.
- User selected proposed region merge for `managed-regions` and apply blocking for conflicting `generated` files.
- Valid region markers are required for a merge proposal; the proposal warns about local edits and is displayed before confirmation. Malformed markers block apply.
- User selected separately stored full rendered baseline snapshots, referenced and integrity-checked from state.
- When snapshot persistence is disabled, use an unverified two-way diff and still permit confirmed apply.
- `external-link` is documented as not rendered by Ageroot, so it has no newly rendered content version; its role needs an explicit decision.
- External links are validated for existence and expected target only; their target contents are excluded from diff and apply.
- Snapshot persistence is a global `ageroot.config.yaml` setting: `snapshots: enabled|disabled`.
- User selected a summary-first dry-run report. This conflicts with SETUP's stated requirement to present the complete diff before confirmation unless confirmation is deferred until the full diff is requested and shown.
- User chose to change SETUP so summary is sufficient for confirmation; complete diffs remain available on request. This decision likely qualifies for an ADR because it changes the safety boundary through a real UX/safety trade-off.
- Summary is tiered: changed and unchanged are counts only; each conflict or blocked path includes reason, apply eligibility, and full-diff access.
- Apply is atomic: any conflict or blocked path prevents the full update.
- Missing or invalid snapshots require an explicit user decision; no automatic fallback or replacement is allowed.
- Snapshot-integrity escalation offers cancellation or a one-time unverified override; the override does not alter baseline history.
- Snapshots, SHA-256 values, and state commit atomically only after a successful full apply.
- Potential deletion blocks ordinary update and requires a separate explicit confirmation.
- A deletion that targets a locally modified file is blocked until the user manually preserves or relocates the file and repeats dry-run.
- Rendered baseline snapshots live in Git-ignored `.agents/snapshots/`.
- Existing installations with snapshots enabled but no snapshot store use an explicit unverified migration bootstrap; snapshots are created only after successful apply.
- User selected broad normalization that includes Markdown/YAML formatting. Exact permitted transformations remain unresolved because generic formatting can alter YAML ordering, scalar style, or Markdown structure.
- Deterministic normalization removes line endings, final newline, trailing whitespace, and formatter-only Markdown/YAML noise, without changing YAML data/key order or Markdown structure/text.
- Confirmed result classes: `unchanged`, `changed`, `unverified`, `region-merge`, `conflict`, `blocked`, `invalid-link`, and `deletion-pending`. Only `changed`, `unverified`, and `region-merge` are eligible; all other classes block atomic apply.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| No implementation during this design session. | The grilling workflow requires shared understanding before action. |
| Canonical name: safety-first dry-run comparison. | It describes a strategy-aware pre-apply safety assessment rather than a generic file diff. |
| Use a hybrid baseline. | Ageroot owns render history only for renderer-owned strategies. |
| Propose a region merge for `managed-regions`; block generated-file conflicts. | Preserves declared user regions while keeping whole-file conflicts explicit. |
| Require structurally valid region markers. | Only then is the merge deterministic and reviewable. |
| Store rendered baselines separately, with state references and SHA-256. | Enables three-way comparison without inflating state. |
| Allow unverified two-way comparison when snapshots are disabled. | Preserves user choice while making the lost classification explicit. |
| Validate external links only by link state and target. | Ageroot does not own their content. |
| Make snapshot persistence installation-wide. | A single config setting makes storage and classification behavior predictable. |
| Prefer summary-first reporting. | Requires an explicit choice between a two-stage review gate and changing SETUP's approval protocol. |
| Make summary sufficient for confirmation. | User accepts the summary-first UX over mandatory pre-confirmation full diffs. |
| Use a tiered confirmation summary. | Show detail only where safety action is required. |
| Require atomic apply. | Prevents a partially updated managed infrastructure set. |
| Escalate snapshot integrity failures to the user. | Keeps an enabled integrity contract from silently degrading. |
| Offer a one-time unverified override. | Allows explicit progress without masking or repairing integrity failures. |
| Commit snapshots and state atomically after apply. | Prevents baseline history from describing a partial update. |
| Escalate potential deletion separately. | A destructive removal must not be bundled into ordinary update approval. |
| Block deletion of locally modified files. | A snapshot is not a user backup. |
| Use Git-ignored `.agents/snapshots/`. | Keep project-local baselines out of version-control history. |
| Use explicit unverified migration bootstrap. | Existing managed content cannot become trusted history silently. |
| Normalize Markdown/YAML formatting broadly. | Requires an explicit transform allowlist before comparison is safe. |
| Use deterministic formatter-only normalization. | Remove cosmetic noise without a lossy semantic comparison. |
| Use fixed result classes and eligibility. | A summary and atomic gate need an exhaustive, unambiguous vocabulary. |
| Record summary-first confirmation in ADR-0001. | The decision changes a safety boundary through a non-obvious UX/safety trade-off. |
| Correct Hybrid baseline glossary definition. | External links are validation-only and have no rendered content baseline. |
| Use Orca full handoff for implementation. | User explicitly requested Orca for Antigravity. |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| No root CONTEXT.md or ADR directory exists. | Create lazily once terminology or a qualifying durable trade-off is resolved. |
| Truncated patch command | No changes were made; repeated with a complete patch. |
| Second truncated patch command | No changes were made; repeated with a complete patch. |
| Orca runtime open timeout | Orca desktop window did not become available; protocol forbids fallback delegation. |
| Repeated Orca runtime open timeout | Runtime remains `stale_bootstrap` and disconnected. |
| Third truncated patch command | No changes were made; split the retry into short patches. |
| Fourth truncated patch command | No changes were made; split the retry into short patches. |

## Resources

- `.agents/SETUP.md`
- `.agents/ageroot.state.yaml`
- `.agents/memory/DECISIONS.md`
