# Ageroot management skill separation

**Status:** accepted

Ageroot extracts stack installation, configuration verification, dry-run comparison (`plan`), and atomic update (`apply`) from monolithic runtime agent instructions into a dedicated first-party agent skill: `skills/ageroot/`.

## Context

Previously, setup and update protocols lived inside `.agents/AGENTS.md` (under `## Installation and updates`) and standalone files `.agents/SETUP.md` and `.agents/SKILLS.md`. This increased the default context footprint of `AGENTS.md` during normal development and required agents to interpret long procedural markdown documents rather than executing structured tooling.

## Decision

1. **Dedicated first-party skill**:
   - Authored in `skills/ageroot/` with YAML frontmatter triggers for stack installation, verification, and updates.
   - Deployed to `.agents/skills/ageroot` via APM (`./skills/ageroot` locally and `gsdstr/ageroot/skills/ageroot` in consumer templates).
2. **CLI execution surface**:
   - Exposes `skills/ageroot/scripts/ageroot.py` providing `check`, `plan`, and `apply` subcommands wrapping `packages/ageroot_core` (Update engine and distribution service).
   - Keeps APM package management (`apm install`, `apm add`, `apm remove`) external to the skill, preserving separation of concerns.
3. **Payload and documentation relocation**:
   - Moves `SETUP.md` and `SKILLS.md` into `skills/ageroot/references/`.
   - Removes standalone `SETUP.md` and `SKILLS.md` rules from `packages/ageroot_core/distribution/manifest.py`, pruning them from `.agents/ageroot.state.yaml` and baseline snapshots.
   - Removes `## Installation and updates` from `templates/core/.agents/AGENTS.md` and `.agents/AGENTS.md`, replacing it with a concise pointer under `## Agent skills`.
4. **Testing**:
   - Adds `tests/test_ageroot_skill.sh` covering `check`, `plan`, and `apply` against isolated targets, integrated into the repository test runner.
