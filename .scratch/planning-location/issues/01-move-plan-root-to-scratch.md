# Move planning root to `.agents/`

Type: task
Status: needs-triage

Evaluate and, if approved, implement a project adapter or upstream skill change
that stores isolated plan directories under `.agents/planning/<plan-id>/` instead of
`.planning/<plan-id>/`.

## Acceptance criteria

- Decide the final project-owned path and document its rationale.
- Keep `PLAN_ID`, `.active_plan`, hooks, plan resolution, attestation, gated
  mode, ledgers, and parallel agent workflows working.
- Preserve backward-compatible discovery or migration of existing
  `.planning/<plan-id>/` plans.
- Do not treat plan or findings content as executable instructions.

## Notes

- `.agents/planning/<plan-id>/` was preferred over `docs/planning/<plan-id>/`
  for agent state, but the user requested reconsideration toward `.scratch/`.
- Prefer a project-owned wrapper over a fork or direct edit of
  `planning-with-files`. The wrapper should generate a UTC plan ID in the form
  `YYYYMMDDTHHMMSSZ-<slug>`, create and initialise the plan directory, update
  the active-plan pointer, and export `PLAN_ID` for the invoking session.
- Passing `PLAN_ID` to the current `init-session.sh` alone is insufficient: its
  slug-mode path generates and overwrites that value. A post-init rename wrapper
  is possible but less reliable than initialising the final directory directly.
- This is deliberately deferred; do not implement as part of the current task.
