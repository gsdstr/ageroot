# Ageroot

Control repository for Ageroot, personal drop-in agent infrastructure.

## Contents

- `as_template/` — copyable Ageroot template: agent instructions, setup,
  skills policy, and portable protocols.
- `as_memory-skills/` — development source and tests for memory-lifecycle
  skills.
- `docs/agents/` — local issue-tracking, triage, and domain-documentation
  conventions.

## Use

Copy `as_template/` into a new repository, set
`.agents/ageroot.config.yaml`, then follow `.agents/SETUP.md`.
