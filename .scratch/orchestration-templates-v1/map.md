# Neutral orchestration templates v1 — decision map

Status: resolved
Label: wayfinder:map

## Destination

Produce a v1 specification and role maps for neutral orchestration templates.
They must cover the complete task lifecycle, the agents Antigravity, Codex,
Hermes and Pi, and models accessible through the user's Antigravity and
ChatGPT subscriptions. This map does not implement a runnable orchestrator.

## Notes

- Domain: portable agent orchestration. Describe roles independently from any
  one agent; bind defaults and fallbacks separately.
- Model choice uses capability profiles (`fast`, `reasoning`, `coding`,
  `review`) plus a replaceable local inventory rather than hard-coded names.
- V1 contains four phase templates (intake, research/planning, implementation,
  review/integration) and one end-to-end composition map.
- Human gates: start, plan-to-implementation, final integration, agent
  conflict, missing access, irreversible action, and breached iteration or
  cost-plan limits.
- Use `grilling` and `domain-modeling` when resolving decision tickets.
- The local Markdown tracker is canonical for this map.

## Decisions so far

<!-- Closed ticket summaries appear here. -->

- [Define orchestration role contract and vocabulary](issues/01-role-contract-and-vocabulary.md): Use seven agent-neutral roles (Owner, Coordinator, Researcher, Author, Builder, Reviewer, Integrator) and a nine-field role-card contract; record the vocabulary in `CONTEXT.md`.
- [Record subscription-accessible model inventory](issues/02-subscription-model-inventory.md): Record core Antigravity (Gemini) and ChatGPT (Codex) subscription models in a local inventory, exclude low-limit Claude options, map to four capability profiles, and establish two-tier quota fallback.
- [Define budget, iteration, and human-gate policy](issues/03-budget-iteration-and-human-gates.md): Use a composite budget, 80% warning/100% hard gate, three iteration and Builder–Reviewer-cycle limits, a standard profile, and a shared Owner decision-packet contract.
- [Specify neutral template package and lifecycle composition map](issues/05-neutral-template-package-and-lifecycle-map.md): Define 7-field phase template schema across 4 phases, linear lifecycle map with Owner gates and two-tier loopback, planning-with-files compatible handoffs, Reviewer-blocking conflict rule, and distribution in templates/orchestration/v1/ and ageroot_template/.agents/orchestration/.
- [Assign default agents and model capability profiles to roles](issues/04-default-agent-and-model-assignments.md): Bind six agent roles across Antigravity and Codex subscriptions, enforce orthogonal Builder/Reviewer pairings (agy/codex), and set Hermes/Pi as Tier-3 emergency fallbacks requiring Owner decision packets.

## Not yet specified

- How a future runtime adapter should translate the neutral specification;
  adapters are outside v1.

## Out of scope

- Implementing or operating an orchestration runtime.
- Buying additional model subscriptions or depending on API credentials not
  included in the user's current subscriptions.
