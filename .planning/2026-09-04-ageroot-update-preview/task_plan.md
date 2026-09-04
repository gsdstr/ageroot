# Task Plan: Ageroot Update Preview

## Goal

Render the updated local Ageroot template and deliver a safety-first, non-mutating comparison for explicit user approval.

## Next Step

Wait for user direction on the blocked state-model migration; do not apply any Ageroot changes. Apply metadata-only and `.planning/` exclusion rules in any future dry-run.

## Current Phase

Phase 3

## Phases

### Phase 1: Requirements & Discovery

- [x] Read repository, portable-agent, permissions, setup, and state instructions.
- [x] Inspect worktree and template inventory.
- **Status:** complete

### Phase 2: Render and Compare

- [x] Render all state-managed template paths from current configuration.
- [x] Validate external links and classify every managed path.
- [x] Produce complete unified diff.
- **Status:** complete

### Phase 3: Delivery

- [x] Report paths, classifications, blockers, and confirmation request.
- **Status:** complete

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use an isolated `.planning` plan | Required project workflow; no Ageroot-managed path, state, snapshot, template, or user-owned file will be modified. |
| Treat snapshot-less state as unverified | `snapshots: enabled` but legacy state supplies no snapshot references/hashes, as defined by `SETUP.md`. |
| Render only generated metadata marker values | Template placeholder examples in documentation are literal examples, not render inputs. |
| Block atomic update | `.agents/protocols/` is a directory state entry that the supplied comparison runtime cannot read or snapshot; update must remain atomic. |
| Exclude `.planning/` and ignore metadata-only marker changes | User-directed dry-run scope and classification rules. |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| None | 1 | N/A |
