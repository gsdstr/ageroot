# Add portable Orca runbook and configuration

Status: resolved
Assignee: /root

Spec: [Orca orchestration adapter v1](../spec.md)

## Scope

Add portable `.agents/orchestration/orca/` documentation and the AGENTS.md
opt-in block. Document verified Orca Run/Task/Dispatch, decision Task,
worktree, audit, recovery, and explicit-mode rules. Preserve `neutral` as the
default and do not invoke Orca.

## Acceptance criteria

- AGENTS.md exposes availability, default, package/audit paths, and request override.
- Runbook maps four phases to Tasks, role work to Dispatches, and gates to blocked decision Tasks.
- Runbook covers read-only Reviewer, path-owned child worktrees, and no automatic branch deletion.
- No Orca state changes occur.

## Dependencies

None.

## Resolution

Added opt-in adapter configuration to template AGENTS.md and portable
`.agents/orchestration/orca/RUNBOOK.md`. The runbook documents mapping,
decision Tasks, dry-run/apply/execute safety, worktree/reviewer policy, and
audit/recovery without invoking Orca.
