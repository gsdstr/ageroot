---
name: ageroot
description: Install, configure, dry-run, and update the Ageroot agent-infrastructure stack. Use for "install ageroot", "update ageroot", "dry run update", "check ageroot", or reviewing configuration and state.
---

# Ageroot skill

Use this skill to configure, verify, dry-run, and update the portable Ageroot agent infrastructure in a repository.

## Triggers

Use when the user asks to:
- Check Ageroot stack integrity or detect drift (`check ageroot`, `ageroot status`)
- Run a dry-run comparison of pending template updates (`dry run update`, `ageroot plan`)
- Apply approved updates to the Ageroot stack (`update ageroot`, `ageroot apply`)
- Install or bootstrap Ageroot in a target repository (`install ageroot`, `setup ageroot`)

Do not use this skill for APM package management (`apm install`, `apm add`, `apm remove`); use direct `apm` CLI commands for skill packages.

## Safety and mutation boundary

- Always run `plan` (dry run) and present a summary-first confirmation report before executing `apply`.
- Never execute `apply` if the dry run reports `conflict`, `blocked`, or `invalid-link`.
- Files pending deletion require explicit deletion confirmation (`--allow-deletions`).
- Rendered baseline snapshots are verified against SHA-256 hashes before apply. Any snapshot corruption triggers escalation.
- Apply is atomic: either all eligible files succeed and commit new snapshot state in `.agents/ageroot.state.yaml`, or none do.

## Workflow commands

The skill runner is located at `scripts/ageroot.py` (or `.agents/skills/ageroot/scripts/ageroot.py` when deployed).

```bash
RUNNER=skills/ageroot/scripts/ageroot.py

# 1. Check for drift against canonical templates
python3 "$RUNNER" check

# 2. Safety-first dry run comparison (plan)
python3 "$RUNNER" plan

# 3. Atomic apply after user confirmation
python3 "$RUNNER" apply

# 4. Atomic apply with confirmed deletions
python3 "$RUNNER" apply --allow-deletions

# 5. Reconstruct missing snapshots from workspace after git clone
python3 "$RUNNER" snapshot-sync
```

## References

Detailed protocol and historical guides:
- [Ageroot Setup and Updates Protocol](references/SETUP.md): comprehensive dry-run comparison, snapshot persistence, and render strategies.
- [Project Skills Reference](references/SKILLS.md): APM manifest conventions and requirements.
