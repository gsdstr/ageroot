# Ageroot

Unified monorepo for Ageroot portable agent infrastructure.

## Contents

- `packages/ageroot_core/` — core engine: safety-first Update engine and reproducible Distribution module.
- `skills/` — first-party skills (`ageroot`, `memory-manager`, `memory-maintenance`) and their lifecycle test suites.
- `templates/` — canonical templates: base instructions (`templates/core/`), neutral portable orchestration package (`templates/orchestration/v1/`), and Orca adapter (`templates/orchestration/orca/`).
- `docs/` — architectural decisions (ADRs) and migration provenance (`docs/PROVENANCE.md`).
- `scripts/` — consolidated test suite runner (`scripts/test.sh`) and sync tooling.

## Development & Testing

Run all test suites (core comparison, distribution drift, orchestration sync, and memory skills):

```sh
./scripts/test.sh
```

## Distribution & Export

Export a clean, self-contained distribution payload for a consumer project:

```sh
# Export default payload (core + neutral orchestration + orca adapter)
python3 -m ageroot_core.distribution --export /path/to/consumer

# Export with opt-in first-party memory skills
python3 -m ageroot_core.distribution --export /path/to/consumer --components core,orchestration,orca_adapter,memory

# Check whole-payload drift
python3 -m ageroot_core.distribution --check --target /path/to/consumer
```
