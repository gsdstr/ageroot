---
name: ageroot-orchestrate
description: Coordinate a task across intake, research and planning, implementation, and review and integration with Owner gates and budgets. Use for /ageroot-orchestrate or an end-to-end multi-role lifecycle.
---

# Task orchestration

1. Read `manifest.yaml`, `lifecycle-map.md`, and the current phase under
   `phases/`. These define lifecycle authority, handoffs, Owner gates, budget
   allocation, and rework loops. Validate the package with
   `python3 <this-skill>/scripts/validate.py --package`.
2. Record objective, acceptance evidence, scope, mode, resource budget, and
   phase state in an isolated `.planning/<plan-id>/`. Owner retains budget
   authority and final acceptance; Coordinator owns lifecycle and plan state.
3. Before each role assignment, use `/ageroot-roles`:
   `python3 <skills-dir>/ageroot-roles/scripts/roles.py resolve <role> --workspace <root>`.
   Record winning layer, target, and rejection trace. Resolve `unavailable`
   with the Owner; do not bypass an explicit disabled or exhausted role.
4. Complete phases in manifest order. Each handoff must satisfy its declared
   schema, entry/exit criteria, and producing/consuming role contracts. Owner
   decisions are mandatory at Start, Plan-to-Build, and Final Acceptance.
   Pause affected branches at gates; independent branches may continue within
   their own scope and budget.
5. Enforce Reviewer independence before dispatch: resolve Reviewer with
   `--exclude-model <builder-model> --exclude-family <builder-family>` using
   Builder resolution's `family`, then isolate Reviewer in a read-only worker
   context. Stop if orthogonality cannot be established. Builder self-review
   does not satisfy the gate.
6. Track iterations, turns, model-capability units, and any wall-clock limit.
   At 80%, report actual versus planned usage, forecast, and a reduction option.
   At 100%, start no new task/iteration until Owner re-baselines, reduces scope,
   or stops work. Default per-output and Builder–Reviewer rework limits are
   three; apply Owner overrides recorded in the plan.
7. Integrate accepted artifacts, record verification and unresolved risks, and
   produce the release packet for Owner Final Acceptance. Completion requires
   recorded acceptance and all required handoffs, not merely finished coding.

Candidate traversal is allowed only before execution begins. After an agent
starts a turn, modifies files, or incurs usage, reconcile failure and partial
artifacts explicitly before any replacement dispatch.

For explicit `mode: orca`, read `orca/RUNBOOK.md` and start with
`orca/adapter.py --plan-id <id> --workspace <root>` in dry-run mode. Orca
supplies supervised execution state; these phase templates retain policy
ownership. Neutral mode uses the same contracts without Orca calls.
