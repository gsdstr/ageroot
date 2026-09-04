# Add a wrapper for timestamped plan IDs

Type: task
Status: needs-triage

Add a project-owned wrapper around the `planning-with-files` plan
initialisation workflow. It must generate IDs in UTC using
`YYYYMMDDTHHMMSSZ-<slug>` without modifying or forking the installed skill.

## Acceptance criteria

- Generate a valid UTC `PLAN_ID` in the required format.
- Initialise the final plan directory directly; do not rely on renaming a
  directory after `init-session.sh` has run.
- Create the standard planning artifacts from the skill templates.
- Update the active-plan pointer and export `PLAN_ID` for the invoking session.
- Preserve collision handling for plans created in the same second.
- Document invocation and compatibility with plan resolution, hooks,
  attestation, ledgers, and parallel sessions.

## Notes

- Passing `PLAN_ID` to the current `init-session.sh` alone does not work: its
  slug-mode path overwrites the variable.
- Keep this wrapper independent of issue 01, which evaluates moving the plan
  root to `.scratch/`.
