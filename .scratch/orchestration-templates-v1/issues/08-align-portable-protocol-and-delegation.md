# Align portable protocol and delegation matrix

Status: resolved
Assignee: /root
Blocked by: 06, 07

Spec: [Neutral orchestration templates v1](../spec.md)

## Scope

Reconcile existing `ageroot_template/.agents/protocols/orchestration.md` with the implemented package. Update `ageroot_template/.agents/protocols/delegation.md` so neutral orchestration points to the lifecycle and Owner gates. Do not overwrite unrelated protocol rules.

## Acceptance criteria

- Protocol names canonical roles, capability-profile assignment/fallback policy, standard budget, gates, and lifecycle.
- Delegation matrix directs lifecycle work to portable orchestration protocol.
- Protocol paths, phase names, handoffs, and gates match implemented package exactly.
- Unrelated delegation modes remain unchanged.

## Dependencies

- [Scaffold orchestration package and schemas](06-scaffold-package-and-schemas.md)
- [Author phase templates and lifecycle map](07-author-phase-templates-and-lifecycle-map.md)

## Resolution

Aligned the portable orchestration protocol with the source package contract:
source and portable paths, manifest/phases/lifecycle/schemas contents, the
seven-field phase contract, handoff and budget requirements, intra- and
cross-subscription fallback, and Tier-3 Hermes/Pi authorization. Updated the
delegation matrix so end-to-end lifecycle work enters through the portable
manifest, phases, lifecycle map, and Owner gates.

Discovered that the portable package directory itself has not yet been
distributed. Created [Distribute portable orchestration template package](10-distribute-portable-orchestration-package.md) and made final validation
depend on it.
