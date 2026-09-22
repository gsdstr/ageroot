# Neutral orchestration templates v1

Status: ticketed

## Goal

Specify a portable, runtime-neutral orchestration-template package for a full task lifecycle. The package maps agent-neutral roles to the Owner's Antigravity and ChatGPT subscription surfaces, governs resource use and human decisions, and can be statically validated without an orchestration runtime.

## Scope

- Seven roles: Owner, Coordinator, Researcher, Author, Builder, Reviewer, Integrator.
- Four phase templates: intake, research/planning, implementation, review/integration.
- One lifecycle map, model assignments, budget/gate policy, Markdown/YAML contracts, JSON Schemas, and portable protocol documentation.

## Non-goals

- Runtime/host adapter implementation or deployment.
- New subscriptions or credentials outside active Antigravity and ChatGPT subscriptions.
- Antigravity Claude models, due to restrictive subscription quotas.

## Roles and role cards

`CONTEXT.md` defines the canonical vocabulary. Every role card contains `Mission`, `Responsibilities / Non-goals`, `Inputs / Outputs`, `Authority`, `Owner gates`, `Acceptance criteria`, `Default assignment / fallback`, `Limits`, and `Escalation triggers`.

One harness may hold several roles. For risk-bearing artifacts, Reviewer cannot share Builder's harness or model family.

## Models and fallbacks

[`model-inventory.md`](model-inventory.md) is the replaceable model inventory. Each entry supplies model id, display name, provider surface, context window, tool mode, capability profiles, and intra-surface quota fallback.

| Role | Profile | Default | Intra-surface fallback | Cross-surface fallback |
| --- | --- | --- | --- | --- |
| Owner | human | Human user | — | — |
| Coordinator | fast / reasoning | agy Gemini Flash High | agy Gemini Flash Medium | codex GPT-5.6 Sol |
| Researcher | reasoning | agy Gemini Pro High | agy Gemini Flash High | codex GPT-6 Astra |
| Author | reasoning / fast | codex GPT-5.6 Sol | codex GPT Reserve | agy Gemini Pro High |
| Builder | coding | agy Gemini Flash High | agy Gemini Flash Medium | codex GPT-5.6 Terra |
| Reviewer | review | codex Auto Review or GPT-5.6 Terra | codex GPT Reserve | agy Gemini Pro High |
| Integrator | coding / fast | agy Gemini Flash High | agy Gemini Flash Medium | codex GPT-5.6 Terra |

Intra-subscription fallback is automatic. Cross-subscription fallback pauses the affected branch and needs an Owner decision packet. Hermes and Pi are Tier-3 emergency fallbacks; metered use requires Owner approval.

## Budget and gates

| Dimension | Default |
| --- | ---: |
| Run-level iterations | 12 |
| Iterations per role/output | 3 |
| Builder–Reviewer rework cycles | 3 |
| Agent turns | 30 |
| Model-capability units | 100 |
| Wall-clock time | 120 minutes |
| Warning / hard gate | 80% / 100% |

Model-capability units are actual token cost where available, otherwise configured capability weights. At 80%, Coordinator reports plan/actual, forecast, and a reduction option. At 100%, no new task or iteration starts until Owner re-baselines, reduces scope, or stops.

Every human gate carries context, options, recommendation, and projected scope/budget/risk impact. Gates: task start, plan-to-build, final acceptance, conflict, missing access, irreversible action, and hard limit breach. Only the affected branch pauses.

## Package layout

```text
templates/orchestration/v1/
  manifest.yaml
  phases/01-intake.md
  phases/02-research-planning.md
  phases/03-implementation.md
  phases/04-review-integration.md
  lifecycle-map.md
  schemas/
ageroot_template/.agents/orchestration/
ageroot_template/.agents/protocols/orchestration.md
```

Update `ageroot_template/.agents/protocols/delegation.md` with the neutral delegation matrix.

`manifest.yaml` declares version `1.0.0`, every template, and schema bindings. Each Markdown phase declares YAML frontmatter fields: `metadata`, `participating_roles`, `entry_criteria`, `exit_criteria`, `handoff_artifacts`, `budget_slice`, and `escalation_gates`.

## Lifecycle and handoffs

```text
01 intake → 02 research/planning → 03 implementation → 04 review/integration
```

Owner gates are Start, Plan-to-Build, and Final Acceptance. Minor defects may loop back within the remaining budget. Architecture changes, scope expansion, unresolved review, and limit breaches must escalate through an Owner decision packet.

| Artifact | Producer → Consumer | planning-with-files target |
| --- | --- | --- |
| `task_brief.md` | Owner + Coordinator → Researcher/Author | Seeds `task_plan.md` goals and limits |
| `task_spec.md` | Researcher + Author → Builder | Adds phases and finding links to `task_plan.md` |
| `implementation_manifest.md` | Builder + Reviewer → Integrator | Worker, diff, and test facts in `progress.md` |
| `release_packet.md` | Integrator + Reviewer → Owner | Output, verification, acceptance audit in `progress.md` |
| `change_request.md` | Coordinator → affected roles | Deficit, affected files, proposed change |

Reviewer blocks quality/correctness failures. After three unresolved Builder–Reviewer cycles, Coordinator escalates to Owner and may not override Reviewer.

## Acceptance criteria

- Manifest declares every template and schema binding.
- Every phase has seven contract fields and valid canonical roles.
- Every lifecycle edge has compatible producer/consumer handoffs.
- Budget slices stay within the run profile.
- Owner gates and escalation triggers are declared.
- Builder/Reviewer assignments retain harness/model-family independence.
- Handoffs name planning-with-files targets.
- Protocol documentation matches roles, budget, gates, fallback policy, and lifecycle.

## Decision sources

- [Define orchestration role contract and vocabulary](issues/01-role-contract-and-vocabulary.md)
- [Record subscription-accessible model inventory](issues/02-subscription-model-inventory.md)
- [Define budget, iteration, and human-gate policy](issues/03-budget-iteration-and-human-gates.md)
- [Assign default agents and model capability profiles to roles](issues/04-default-agent-and-model-assignments.md)
- [Specify neutral template package and lifecycle composition map](issues/05-neutral-template-package-and-lifecycle-map.md)
