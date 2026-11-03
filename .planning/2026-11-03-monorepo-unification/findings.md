# Findings: Monorepo Unification and Distribution Module

- `ageroot_template` commit at migration: `1fb3c55` (remote: `https://github.com/gsdstr/ageroot_template.git`).
- `ageroot_skills` commit at migration: `2508bdc` (remote: `https://github.com/gsdstr/ageroot_skills.git`).
- Initial control repo commit: `5392df2`.
- Update engine requires `renders: dict[str, str]` (relative file paths mapped to file content).
- Existing `ageroot.state.yaml` in template had directory path `.agents/protocols/` which causes mismatch; distribution module must expand all directory items to file paths.
- Orca adapter files (`orca/RUNBOOK.md`, `orca/adapter.py`) must be declared under `orca_adapter` component in manifest to avoid drift error during neutral package check.
