# Evaluate automatic maintenance invocation options

Type: research
Status: needs-triage

Spec: [Ageroot memory skills](../spec.md)

## Problem

The first version runs memory-maintenance through an explicit command outside
active task work. Decide whether additional triggers improve upkeep without
racing working sessions or making cleanup behavior unclear.

## Options to compare

- Continue using only the explicit command as the baseline.
- Invoke maintenance on supported host session-end events.
- Run a separate scheduled command/process using an appropriate host scheduler.

## Acceptance criteria

- Compare portability, reliability, operating cost, installation/update burden
  and behavior when no agent session or working directory is available.
- Verify actual session-end delivery guarantees and scheduler requirements;
  do not infer reliable shutdown execution from upstream comments alone.
- Define eligible projects, data-root resolution, runtime-version selection,
  cadence and conditions for skipping a run.
- Address overlap with workflow appends, concurrent maintenance, missed runs,
  interruption, retries and failure reporting. Preserve the core concurrency
  contract because maintenance can rewrite journals.
- Explain how users enable/disable automation and inspect execution results.
- Reuse the explicit maintenance entry point and single manager-owned runtime;
  do not add another runtime copy or automatic knowledge acceptance.
- Produce an evidence-backed recommendation with tradeoffs and follow-up
  implementation scope. If a prototype is needed, use disposable data only.

## Dependencies

The explicit maintenance command and its behavior must be stable before
turning on any automatic trigger. Host logging hooks are tracked separately in
[issue 01](01-memory-hooks.md).

## Comments

- Requested during the memory design interview. Explicit invocation remains
  the initial-version policy. This research issue installs no scheduler and
  activates no session-end behavior.
