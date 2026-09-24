# Bridge coordinator event loop

Status: ready-for-agent
Assignee: /root
Blocked by: 03

Spec: [Orca orchestration adapter v1](../spec.md)

## Scope

Orca writes worker messages (`ask`, `heartbeat`, `escalation`, `worker_done`) to
its internal database/inbox, not to the native Antigravity message bus. When the
coordinator dispatches a worker with `worker-start`, it must not yield control
back to the human user or end the turn.

Instead, the coordinator must continuously execute the blocking wait loop:
`orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms <n>`.
Incoming questions (`ask`) must be answered via `orca orchestration reply`
immediately, preventing 10-minute worker timeouts and unnecessary escalations.

## Acceptance criteria

- Coordinator runbook explicitly mandates staying in the check loop post-dispatch.
- Coordinator maintains active supervision while dispatched workers are active.
- Questions (`question`) from `ask` are answered immediately via `reply --id`.
- Every message in a Delivery batch is processed before acknowledging with `--ack <delivery_id>`.
- Settled workers are processed (`worker_done`, release/retain) before acknowledging Delivery.
- Adapter tool/scripts emit the wait loop command as an essential part of execution flow.

## Dependencies

- [Add explicit apply and execute gates](03-add-explicit-apply-execute-gates.md)
