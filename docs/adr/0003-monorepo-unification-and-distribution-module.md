# Monorepo unification and Distribution module

**Status:** accepted

Ageroot unifies canonical source templates, Update engine, first-party skills, tests, and release tooling into a single Git repository. The authoring sources are consolidated under `packages/ageroot_core/`, `skills/`, `templates/`, and `tests/`, while the root `.agents/` directory is maintained strictly as an operational dogfood installation.

History from prior repositories (`ageroot_template` at `1fb3c55` and `ageroot_skills` at `2508bdc`) is preserved via recorded commit provenance in `docs/PROVENANCE.md` and commit metadata, followed by verified deletion of nested repositories.

A new Distribution module (`ageroot_core.distribution`) discovers canonical assets, expands directory structures into concrete file paths, and renders the exact consumer payload mapping before invoking the Update engine. Neutral orchestration templates and the Orca orchestration adapter are maintained as distinct components in the distribution manifest to eliminate spurious drift errors during `--check`. First-party memory skills are maintained in the monorepo but excluded from the default consumer payload, remaining an explicit opt-in distribution component.
