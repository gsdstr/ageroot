# Distribute portable orchestration template package

Status: resolved
Assignee: /root
Blocked by: 08

Spec: [Neutral orchestration templates v1](../spec.md)

## Scope

Make `ageroot_template/.agents/orchestration/` contain the portable
distribution of the validated source package: manifest, four phase templates,
lifecycle map, schemas, validator/readme where applicable. Establish a
repeatable synchronization or verification mechanism so the source and
template distributions cannot silently diverge.

## Confirmed design

- `templates/orchestration/v1/` is the canonical source; the portable package
  is an exact self-contained distribution under
  `ageroot_template/.agents/orchestration/`.
- Distribution includes `manifest.yaml`, `phases/`, `lifecycle-map.md`,
  `schemas/`, `scripts/validate.py`, and `README.md`; development `tests/`
  remain only in canonical source.
- The sync tool defaults to read-only `--check`; explicit `--write` performs
  the mirror. Synchronization is neither automatic nor an install-time
  runtime feature.

## Acceptance criteria

- Portable directory contains every contract referenced by its protocol.
- Source and portable package declare identical manifest, phases, lifecycle,
  schemas, and validation behaviour.
- A local command detects divergence without network access.
- The distribution does not introduce a runtime adapter or overwrite unrelated
  template files.

## Dependencies

- [Align portable protocol and delegation matrix](08-align-portable-protocol-and-delegation.md)

## Resolution

Added `scripts/sync-orchestration-package.py`. Its default and explicit
`--check` modes report source-to-portable drift; `--write` mirrors only the
confirmed allowlist and preserves unknown target files as reported drift.

Created the portable distribution under
`ageroot_template/.agents/orchestration/` with manifest, four phases,
lifecycle map, schemas, validator, and README. The development test suite is
not distributed.

Verified:

```sh
python3 scripts/sync-orchestration-package.py --check
python3 ageroot_template/.agents/orchestration/scripts/validate.py --package
```
