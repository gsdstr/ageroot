# Orca orchestration adapter runbook

Use only when Owner explicitly selects `mode: orca`. Neutral orchestration
templates remain the source of roles, budgets, gates, and handoffs.

## Mapping

- One Owner task → one Orca Run.
- Intake, Research/Planning, Implementation, Review/Integration → four Orca
  Tasks, linked in dependency order.
- A bounded role assignment → Dispatch.
- A human gate → coordinator-owned decision Task. Block dependents until Owner
  structured reply is recorded.

## Safety

- Begin with dry-run. It makes no Orca calls.
- `--apply` creates only disposable Run/Task/DAG state.
- `--execute` is separately explicit and requires recorded Start approval
  before Dispatch or worktree creation.
- One Implementation Task owns one worktree. Overlapping Builder writes are
  serial. Parallel writes need child worktrees after Coordinator path review.
- Reviewer is read-only. Never delete a branch automatically.

## Coordinator event loop

Orca inbox is decoupled from Antigravity's message bus. The coordinator must
maintain active supervision after dispatching a worker:

```bash
# Wait for batch
orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json

# Process all messages in delivery:
# 1. On question (ask): reply immediately
orca orchestration reply --id <message_id> --body "<answer>" --json

# 2. On worker_done: validate output against active dispatch, decide reuse / release / retain
orca orchestration worker-release --dispatch <dispatch_id> --json

# 3. Acknowledge processed batch and resume wait
orca orchestration check --ack <delivery_id> --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json
```

- When receiving `question` (`ask`): reply promptly. Do not let workers stall into timeout.
- When human decision is required: pause branch and present structured Decision Packet to Owner; keep supervision live.
- Acknowledge a Delivery batch (`--ack <delivery_id>`) only AFTER processing its messages.

## Role-to-harness dispatch mapping

Resolve every assignment with the sibling `/ageroot-roles` skill:

```bash
python3 <skills-dir>/ageroot-roles/scripts/roles.py resolve builder --workspace <root>
python3 <skills-dir>/ageroot-roles/scripts/roles.py resolve reviewer --workspace <root> --exclude-model <builder-model> --exclude-family <builder-family>
```

Use resolution JSON `target.harness`, `target.model`, and optional `target.effort`
for agent/model/effort parameters. Record the winning layer and candidate index.
If unavailable, pause and reconcile configuration; never bypass an explicit target
list. Check `unverified` runtime support before dispatch, and verify actual model
access locally. No network/model entitlement is inferred from PATH presence.

`adapter.py` resolves its four phase roles dynamically through the sibling
`ageroot-roles/scripts/roles.py`. Reviewer resolution excludes Builder's
model and family. Its dry-run JSON includes assigned harness/model/effort and
the full resolution evidence; unavailable roles block apply/execute. Keep Reviewer
in an isolated read-only worker context.

When launching Orca workers, inspect the installed runtime's version-matched
orchestration guide and pass the resolved harness/model using supported
agent/model flags (and `--effort <target.effort>` when configured). A CLI-only
harness requires a bound terminal rather than an unsupported agent flag. Reconcile
errors after execution starts explicitly; only pre-dispatch checks may traverse
candidates automatically.

## Audit and recovery

Write `.planning/<plan-id>/orca/run-map.json` and decision packets. Treat Orca
Run/Task state as operational control plane. On an interrupted run, read the
audit trail and Orca task state before any retry; do not recreate a Run or
Dispatch blindly.

