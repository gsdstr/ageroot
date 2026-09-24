# Orca orchestration adapter v1

Status: ticketed

## Goal

Add a portable, opt-in Orca adapter above neutral orchestration templates. It
maps a lifecycle into Orca supervised state while leaving neutral templates as
the authority for roles, budgets, gates, and handoffs.

## Configuration

`AGENTS.md` declares adapter availability, default mode (`neutral`), package
path `.agents/orchestration/orca/`, audit path `.planning/<plan-id>/orca/`, and
Owner request override (`mode: orca` / `mode: neutral`). Request mode overrides
the project default.

## Orca mapping

- One Owner task maps to one Orca Run.
- Intake, Research/Planning, Implementation, Review/Integration each map to
  one Orca Task.
- A bounded role assignment maps to a Dispatch.
- Each human gate maps to a coordinator-owned decision Task; dependent Tasks
  remain blocked until an Owner structured reply is recorded.

## Worktrees and review

One Implementation Task owns one Orca worktree. Overlapping Builder writes are
serial. Parallel write work requires separate child worktrees after Coordinator
path-ownership validation. Reviewer is read-only. Final acceptance never
automatically deletes a branch.

## Adapter surfaces

- Markdown runbook is the canonical operational foundation.
- A thin experimental CLI adapter tests the mapping through Orca CLI; it is not
  a daemon or a replacement lifecycle.
- `--dry-run` is default and makes no Orca calls.
- Explicit `--apply` creates only Run/Task/DAG state.
- Explicit `--execute`, after Owner Start approval, permits worktree and
  Dispatch operations.

## Audit trail

Persist `.planning/<plan-id>/orca/run-map.json` and decision packets.
Orca Run/Task records remain the operational control plane.

## Coordinator event loop

Orca inbox is external to Antigravity message bus. Coordinator must maintain
active supervision of dispatched workers and not abandon the turn:
`orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms <n>`.
Handle `question` (`ask`) immediately via `reply --id`. Validate `worker_done` and
perform settlement accounting before passing `--ack <delivery_id>`. Escalate
human decision gates to Owner with structured Decision Packets.

## Role-to-harness dispatch mapping

Worker dispatch must resolve harness and model from the role card defined in
`protocols/orchestration.md`, preserving model-family independence (e.g. Builder
on `agy`, Reviewer on `codex`). Coordinator must never mechanically pass a
single hardcoded default (`--agent codex` or universal `agy`). Executables must
resolve portably from PATH (`agy`, `codex`, `claude`), never local absolute paths.
In Orca:
- If `--agent <harness>` is supported by Orca runtime, dispatch directly.
- If harness requires custom command or terminal topology, spawn via
  `orca terminal create --command "<harness>"` and bind with `worker-start --terminal <handle>`.

## First acceptance scenario

On a disposable fixture, adapter must produce a full four-phase dry-run, then
explicitly apply only Run/Task/DAG state. It must not dispatch agents or create
worktrees until an explicit `--execute` after the Start gate.

## Acceptance criteria

- Package is portable under `.agents/orchestration/orca/` and referenced by
  AGENTS.md without changing neutral default behavior.
- Runbook accurately documents verified Orca CLI mapping and recovery paths.
- Coordinator maintains supervision loop on Orca inbox; handles `ask`, validates
  `worker_done`, and acknowledges delivery batches.
- Worker dispatch maps harness per role from neutral orchestration contract; preserves
  Builder/Reviewer independence and uses no hardcoded local paths.
- CLI dry-run produces Run, four Tasks, dependencies, gates, and audit plan
  without Orca mutation.
- Apply is explicit and produces only disposable Run/Task/DAG state.
- Execute refuses before Start approval and respects worktree/review policy.
- Audit files map every neutral phase and decision packet to Orca identifiers.
- No daemon, implicit dispatch, implicit worktree, or automatic branch delete.

