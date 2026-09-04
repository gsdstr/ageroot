# Task Plan: File Comparison Strategy

## Goal

Reach a confirmed, precise strategy for Ageroot dry-run comparison that preserves the existing explicit-approval update protocol.

## Next Step

Full implementation handoff completed; worker owns implementation.

## Current Phase

Phase 2: Design the comparison protocol

## Phases

### Phase 1: Discovery and decision framing

- [x] Read update protocol, state, and existing architecture decisions.
- [x] Identify current open question and constraints.
- [x] Resolve the initial decision frontier with the user.
- [x] Resolve the baseline source.
- [x] Resolve conflict policy and apply eligibility.
- [x] Resolve the safety boundary of a proposed region merge.
- [x] Resolve baseline persistence and integrity verification.
- [x] Resolve the comparison behavior when snapshot persistence is disabled.
- [x] Resolve `external-link` comparison and reporting behavior.
- [x] Resolve snapshot-persistence configuration scope.
- [x] Reconcile dry-run report structure with the existing approval protocol.
- [x] Resolve the mandatory fields in the confirmation summary.
- [x] Resolve apply atomicity in the presence of blocked paths.
- [x] Resolve snapshot integrity failure handling.
- [x] Resolve the available user choices in snapshot-integrity escalation.
- [x] Resolve snapshot lifecycle after successful atomic apply.
- [x] Resolve managed-file deletion behavior.
- [x] Resolve deletion behavior for locally modified files.
- [x] Resolve snapshot storage location and version-control policy.
- [x] Resolve snapshot migration behavior.
- **Status:** complete

### Phase 2: Design the comparison protocol

- [x] Define result classes and apply eligibility.
- [x] Capture confirmed domain vocabulary.
- **Status:** complete

### Phase 3: Record durable decisions

- [x] Create or update CONTEXT.md if terminology is confirmed.
- [x] Offer ADR for the summary-first confirmation safety-boundary decision after shared-understanding confirmation.
- [x] Record the approved ADR.
- **Status:** complete

### Phase 4: Confirm shared understanding

- [x] Present the complete strategy and unresolved items.
- [x] Wait for user confirmation before proposing implementation work.
- **Status:** complete

### Phase 5: Orca implementation handoff

- [x] Load Orca handoff instructions and check runtime status.
- [x] Create an independent Antigravity worktree and dispatch the implementation brief through Orca.
- **Status:** complete

## Key Questions

1. What comparison contract should a dry run promise? — Safety-first dry-run comparison.
2. Which artefacts form the baseline for each render strategy? — Hybrid baseline, with separately stored rendered baseline snapshots for renderer-owned files; unverified two-way comparison when snapshots are disabled.
3. How should local modifications be classified and surfaced? — Propose a region merge for `managed-regions`; block conflicting `generated` files.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Preserve explicit approval before apply. | SETUP.md and existing architecture decision require it. |
| Treat Ageroot as a renderer, not a file synchronizer. | Existing accepted architecture decision. |
| Use a safety-first dry-run comparison. | User-selected contract; it must distinguish expected changes, local modifications, and conflicts before apply. |
| Use a hybrid baseline. | Three-way comparison is meaningful for renderer-owned files; external links remain outside Ageroot ownership. |
| Propose a region merge only for `managed-regions`; block conflicting `generated` files. | Preserve declared user regions without treating confirmation as an implicit conflict-resolution choice. |
| Generate and display a proposed region merge only when markers validate; warn about local edits. | The result is deterministic and reviewable. Malformed markers block apply. |
| Store full rendered baseline snapshots separately; state records a reference and SHA-256. | Three-way classification requires prior content while state stays compact and verifiable. |
| With snapshots disabled, show an unverified two-way diff and permit apply after confirmation. | Users can opt out of content retention while being told that local edits cannot be classified. |
| Validate external links by link state and expected target only. | Ageroot does not render, compare, or apply external-link contents. |
| Make snapshot persistence installation-wide via `snapshots: enabled|disabled` in config. | A storage policy is not file-specific; one setting keeps dry-run behavior predictable. |
| Prefer a summary-first dry-run report. | User selected this UX, but it must be reconciled with SETUP's complete-diff-before-confirmation requirement. |
| Make summary sufficient for confirmation; retain full diff on request. | User chose to change SETUP's previous mandatory complete-diff rule. |
| Use a tiered confirmation summary. | Changed and unchanged paths need counts only; conflicts and blocked paths need reason, eligibility, and full-diff access. |
| Require atomic apply. | Any conflict or blocked path prevents a partially updated infrastructure state. |
| Escalate missing or invalid snapshots to an explicit user decision. | No automatic fallback or snapshot replacement may weaken enabled snapshot integrity. |
| Offer cancellation or a one-time unverified override after escalation. | The override is explicitly approved and does not repair or replace baseline history. |
| Commit new snapshots, SHA-256 values, and state only after successful atomic apply. | Baseline history represents complete applied updates only. |
| Block ordinary updates on potential deletion; require separate explicit confirmation. | File removal is a distinct destructive action. |
| Block deletion of a locally modified file. | The user must preserve or relocate it manually before a new dry run. |
| Store snapshots in Git-ignored `.agents/snapshots/`. | Baselines remain project-local without copying generated content into repository history. |
| Bootstrap legacy installations with an explicit unverified confirmation; create snapshots after successful apply. | Existing files are not silently trusted as a baseline. |
| Normalize Markdown/YAML formatting in addition to line endings and trailing whitespace. | User selected broad normalization; the exact permitted transformations remain to be specified. |
| Use deterministic formatter-only Markdown/YAML normalization. | Remove cosmetic noise without hiding data, ordering, structure, or text changes. |
| Use the confirmed fixed result-class vocabulary and eligibility. | `changed`, `unverified`, and `region-merge` are eligible; every other class blocks atomic apply. |
| Use Orca full handoff for implementation. | User explicitly requested delegation through Orca for Antigravity. |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| None | 1 | N/A |
| Truncated patch command | 1 | Reissued a complete patch; no file changes occurred in the failed attempt. |
| Truncated patch command | 2 | Reissued a complete patch; no file changes occurred in the failed attempt. |
| Orca runtime open timeout | 1 | Do not substitute another delegation mechanism; wait for a running Antigravity Orca desktop runtime. |
| Orca runtime open timeout | 2 | Runtime remains `stale_bootstrap`; wait for the user to start a reachable Orca desktop runtime. |
