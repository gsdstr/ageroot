# Author phase templates and lifecycle map

Status: resolved
Assignee: /root
Blocked by: 06

Spec: [Neutral orchestration templates v1](../spec.md)

## Scope

Create four phase templates and `lifecycle-map.md` against the schemas. Encode roles, entry/exit criteria, budget slices, Owner gates, five handoff artifacts, autonomous loopbacks, and escalation loopbacks. Preserve Builder/Reviewer independence and Reviewer blocking authority.

## Acceptance criteria

- All four phase templates validate against their schema.
- Lifecycle order is intake → research/planning → implementation → review/integration, with Start, Plan-to-Build, and Final Acceptance gates.
- Handoffs name producer, consumer, schema, and planning-with-files target.
- Budget slices stay within standard run profile.
- Architecture, scope, review-limit, and hard-limit changes escalate to Owner.

## Dependencies

- [Scaffold orchestration package and schemas](06-scaffold-package-and-schemas.md)

## Resolution

Created four JSON-compatible-YAML phase templates and a lifecycle map. They
declare the seven-field phase contract, all five canonical handoff artifacts,
budget slices totaling the standard profile, mandatory Owner gates, and both
autonomous and escalation loopbacks. The implementation phase preserves
independent Reviewer blocking authority and the three-cycle escalation rule.

Extended the offline validator to load template frontmatter, validate phase
and handoff compatibility, verify aggregate budget, and require the lifecycle
order, gates, and loopbacks.

Verified:

```sh
python3 templates/orchestration/v1/scripts/validate.py --package
python3 -m unittest templates/orchestration/v1/tests/test_validate.py
```
