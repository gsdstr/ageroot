# Build dry-run Orca CLI adapter

Status: resolved
Assignee: /root
Blocked by: 01

Spec: [Orca orchestration adapter v1](../spec.md)

## Scope

Build a thin CLI adapter that loads neutral lifecycle data and emits the
four-phase Orca Run/Task/DAG/decision-Task plan plus
`.planning/<plan-id>/orca/run-map.json` and decision-packet plan. Default mode
is dry-run and makes no Orca calls.

## Acceptance criteria

- Dry-run emits no Orca mutation command.
- Output includes one Run, four Tasks, dependency edges, Owner gates, and audit locations.
- Invalid mode or missing plan id fails with actionable error.
- Tests use a disposable fixture and do not need Orca running.

## Dependencies

- [Add portable Orca runbook and configuration](01-add-portable-orca-runbook-and-config.md)

## Resolution

Added `adapter.py`, which emits an Orca-free four-phase Run/Task/DAG plan,
decision Tasks, and audit locations from a required plan id. It rejects apply
because mutation belongs to the next gated ticket.
