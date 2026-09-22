# Add explicit apply and execute gates

Status: resolved
Assignee: /root

## Resolution

Adapter now exposes explicit `--apply` and `--execute` gates. Apply alone may
invoke Orca Run creation; execute rejects without `--start-approved` and never
implicitly starts workers or creates worktrees. Dry-run retains zero Orca calls.
Blocked by: 02

Spec: [Orca orchestration adapter v1](../spec.md)

## Scope

Add explicit `--apply` and `--execute` paths. Apply creates only disposable
Run/Task/DAG state. Execute refuses before Owner Start approval and only then
permits worktree/Dispatch operations. Record returned Orca identifiers in the
audit trail.

## Acceptance criteria

- Apply and execute are never implicit.
- Apply uses the verified Orca CLI surface and creates no worktree/Dispatch.
- Execute requires recorded Start approval and enforces worktree/reviewer policy.
- Integration test is disposable and includes cleanup instructions without automatic branch deletion.

## Dependencies

- [Build dry-run Orca CLI adapter](02-build-dry-run-cli-adapter.md)
