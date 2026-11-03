# Monorepo Migration Provenance

This document records the provenance of repositories consolidated into the Ageroot monorepo on 2026-11-03 per ADR-0003.

## Source Repositories

### `ageroot_template`
- **Remote**: `https://github.com/gsdstr/ageroot_template.git`
- **Commit SHA**: `1fb3c55fde4caf96146a6031b8806cea759928a9`
- **Commit Subject**: `feat: declare infrastructure and project regions in .agents/AGENTS.md`
- **Target Location**:
  - `packages/ageroot_core/` (from `.agents/ageroot_core/`)
  - `templates/` (base templates and protocols from `.agents/`)
  - Root `package.json` and changesets tooling

### `ageroot_skills`
- **Remote**: `https://github.com/gsdstr/ageroot_skills.git`
- **Commit SHA**: `2508bdc188400e446f18438a18d2f28e274c8f17`
- **Commit Subject**: `feat: extract upstream memory runtime into memory-manager and memory-maintenance skills`
- **Target Location**:
  - `skills/` (`memory-manager/`, `memory-maintenance/`)
  - Upstream source provenance retained in `skills/UPSTREAM.md`
