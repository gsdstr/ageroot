# Findings & Decisions

## Requirements
- User wants reusable orchestration templates for agents, models, and roles.
- Named agents: Antigravity, Codex, Hermes, Pi.
- Model availability is constrained to the user's Antigravity and ChatGPT subscriptions.
- Wayfinder applies: planning first; local Markdown tracker stores map and child decision tickets.
- V1 boundary: specification and role maps only; no implementation.
- Target representation: neutral format.
- Priority scenario: a complete task lifecycle rather than a single phase.
- Role assignments must be agent-neutral with default and fallback agents.
- Models are represented as capability profiles plus a local inventory.
- V1 package has intake, research/planning, implementation, and
  review/integration templates plus a composition map.
- Human gates include lifecycle transitions, risk/conflict conditions, and
  iteration or cost-plan overruns.
- Canonical v1 roles: Owner, Coordinator, Researcher, Author, Builder,
  Reviewer, Integrator. Owner replaces Sponsor; Author owns plans and all
  other non-executable documents.
- Budget is composite: iterations, agent turns, model-capability units, and
  optionally wall-clock time. Model-capability units may carry actual
  token-based cost or a subscription-safe weighted proxy.
- Budget warning is 80% of any finite planned dimension; hard gate is 100%.
  Owner must re-baseline, reduce scope, or stop after a hard gate.
- An iteration is a material output attempt/revision, not an unchanged tool
  retry. Defaults: 3 per role/output and 3 Builder–Reviewer cycles, plus a
  run-level limit set by the plan.
- A human gate pauses only its affected branch. Coordinator sends an Owner a
  decision packet with context, options, recommendation, and impact; all
  lifecycle, risk, and limit gates use this contract.

## Research Findings
- Repository is Ageroot, a portable agent-infrastructure stack; existing domain vocabulary contains no orchestration-template terms.
- Existing ADRs govern update confirmation and memory workflow, not orchestration.
- No relevant project-memory lessons returned for this intent.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Map path convention | `.scratch/<effort>/map.md`, with individual child files in `issues/`, per tracker instructions. |
| Initial map frontier | Role contract, subscription inventory, and budget/iteration/human-gate policy are independent and ready to resolve. |
| Role vocabulary and card shape | Use Owner, Coordinator, Researcher, Author, Builder, Reviewer, Integrator and nine role-card fields; details recorded in issue 01 and CONTEXT.md. |
| Budget, iteration, and gates | Standard profile: 12 run iterations, 3 per role/output, 3 Builder–Reviewer cycles, 30 agent turns, 100 model units, 120 minutes; warning/hard gate at 80%/100%. |
| Model inventory & profiles | Core Antigravity (Gemini) and ChatGPT (Codex) subscription models in local model-inventory.md; Claude models excluded due to low subscription limits; 7-field schema; 4 capability profiles; two-tier quota fallback. |
| Template package & lifecycle map | 7-field phase template schema across 4 phases; linear lifecycle map with Owner Start, Plan-to-Build, and Final Acceptance gates; two-tier loopbacks; planning-with-files handoff alignment; Reviewer blocking arbitration; distribution in templates/orchestration/v1/ and ageroot_template/.agents/orchestration/. |
| Default agent & model assignments | Six agent roles bound across Antigravity and Codex subscriptions; orthogonal Builder/Reviewer rule enforced (Builder on agy -> Reviewer on codex, and vice-versa); Hermes/Pi set as Tier-3 emergency metered fallbacks with Owner decision packets. |
| Buildable specification | `.scratch/orchestration-templates-v1/spec.md` consolidates all five resolved decisions and defines implementation acceptance criteria. |
| Ticket plan | `06` schema scaffold → `07` phase templates/lifecycle → `08` portable protocol alignment → `09` offline package validation. |
| Schema scaffold implementation | Uses JSON-compatible YAML plus Python standard library; validator and five tests cover manifest, unknown role, missing fields, incompatible handoff, and required scaffold paths. |
| Phase template implementation | Four JSON-compatible-YAML templates plus lifecycle map define all handoffs and budget slices. Complete-package validator checks role/handoff compatibility, aggregate budget, order, gates, and loopbacks. |
| Portable distribution gap | Protocol and delegation now name exact portable package contract, but package files are not yet mirrored under `ageroot_template/.agents/orchestration/`; ticket 10 owns distribution and divergence detection. |
| Portable package policy | Use an exact self-contained copy: `templates/orchestration/v1/` is canonical source and `.agents/orchestration/` is its portable distribution. |
| Synchronization policy | `--check` is read-only drift detection; explicit `--write` mirrors canonical source to portable distribution. |
| Portable distribution implementation | `scripts/sync-orchestration-package.py` mirrors an allowlist and preserves unexpected target files as drift; portable validator passes from `ageroot_template/.agents/orchestration/`. |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| Initial planning-skill path was wrong | Used project-local skill path instead. |

## Resources
-
