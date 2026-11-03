# Agent Package Manager (APM) migration

**Status:** accepted

Ageroot replaces `skills-manager` with Microsoft APM (`microsoft/apm`) as the canonical package and dependency manager for agent skills. Skill dependencies and exact content hashes are tracked deterministically in `apm.yml` and `apm.lock.yaml` at repository root, while `apm_modules/` and `.agents/skills/` are excluded from Git via `.gitignore`.

Target materialization is constrained strictly to the `agent-skills` target (`.agents/skills/`), preserving Ageroot's portable single-adapter contract and preventing proliferation of harness-specific folders.

For package dependencies:
- In distributed consumer templates, first-party skills are declared via remote Git repository coordinates.
- In local development within the Ageroot monorepo, local path dependencies (`./skills/...`) are used for dogfooding and iteration without publishing.
- Third-party skills are resolved from remote Git package sources.
