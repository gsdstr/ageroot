# Validate neutral orchestration template package

Status: resolved
Assignee: /root
Blocked by: 06, 07, 08, 10

Spec: [Neutral orchestration templates v1](../spec.md)

## Scope

Run and extend offline static validation over complete package and portable documentation. Exercise valid data plus invalid roles, missing phase fields, bad handoff edges, excessive budget slices, absent Owner gates, and Builder/Reviewer self-review violation. Document commands and results.

## Acceptance criteria

- Valid source templates and lifecycle map pass static validation.
- Each listed invalid case fails with actionable error.
- Validation confirms manifest/schema bindings and planning-with-files targets.
- No implementation creates an orchestration runtime adapter.

## Dependencies

- [Scaffold orchestration package and schemas](06-scaffold-package-and-schemas.md)
- [Author phase templates and lifecycle map](07-author-phase-templates-and-lifecycle-map.md)
- [Align portable protocol and delegation matrix](08-align-portable-protocol-and-delegation.md)

## Resolution

Extended offline validation and its standard-library tests to cover the full
source and portable package. Negative cases reject unknown roles, missing
phase fields, incompatible handoffs, excessive aggregate budgets, missing
Owner gates, and a disabled Reviewer-independence policy. The portable copy is
synchronized after validation and is itself validated offline.

Verified:

```sh
python3 templates/orchestration/v1/scripts/validate.py --package
python3 -m unittest templates/orchestration/v1/tests/test_validate.py
python3 scripts/sync-orchestration-package.py --check
python3 ageroot_template/.agents/orchestration/scripts/validate.py --package
```
