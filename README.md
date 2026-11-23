# Ageroot

Unified monorepo for Ageroot portable agent infrastructure.

## Contents

- `packages/ageroot_core/` — core engine: safety-first Update engine and reproducible Distribution module.
- `skills/` — first-party skills (`ageroot`, `ageroot-orchestrate`, `ageroot-roles`, `memory-manager`, `memory-maintenance`) and their lifecycle test suites.
- `templates/` — canonical base instructions and consumer configuration (`templates/core/`).
- `docs/` — architectural decisions (ADRs) and migration provenance (`docs/PROVENANCE.md`).
- `scripts/` — consolidated test suite runner (`scripts/test.sh`) and sync tooling.

## Development & Testing

Run all test suites (core comparison, distribution drift, orchestration and role routing, and memory skills):

```sh
./scripts/test.sh
```

## Distribution & Export

Export a clean, self-contained distribution payload for a consumer project:

```sh
# Export default payload (core + orchestration skill (including Orca adapter) + role routing skill)
PYTHONPATH=packages python3 -m ageroot_core.distribution --export /path/to/consumer

# Export with opt-in first-party memory skills
PYTHONPATH=packages python3 -m ageroot_core.distribution --export /path/to/consumer --components core,ageroot-orchestrate,ageroot-roles,memory

# Check whole-payload drift
PYTHONPATH=packages python3 -m ageroot_core.distribution --check --target /path/to/consumer
```
