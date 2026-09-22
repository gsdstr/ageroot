# Scaffold orchestration package and schemas

Status: resolved
Assignee: /root

Spec: [Neutral orchestration templates v1](../spec.md)

## Scope

Create `templates/orchestration/v1/` with `manifest.yaml` at version `1.0.0`, a `phases/` directory, `lifecycle-map.md`, and `schemas/`. Define JSON Schemas for the manifest, seven-field phase frontmatter, lifecycle map, and handoff contracts. Provide an offline static-validation entry point.

## Acceptance criteria

- Manifest declares version, four phase templates, lifecycle map, and schema bindings.
- Schemas reject an unknown canonical role, missing required phase field, and incompatible handoff producer/consumer declaration.
- Validation has a documented local command and requires neither network nor runtime.
- New source paths are limited to `templates/orchestration/v1/` and required test/support paths.

## Dependencies

None.

## Resolution

Created `templates/orchestration/v1/` with manifest `1.0.0`, phase and
lifecycle scaffolds, four JSON Schemas, an offline Python validator, and five
standard-library unit tests. The manifest is JSON-compatible YAML to avoid a
YAML dependency. Validation commands are documented in the package README.

Verified:

```sh
python3 templates/orchestration/v1/scripts/validate.py --schema-smoke-test
python3 -m unittest templates/orchestration/v1/tests/test_validate.py
```
