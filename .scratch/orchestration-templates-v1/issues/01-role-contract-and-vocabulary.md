# Define orchestration role contract and vocabulary

Type: grilling
Status: resolved
Assignee: /root

## Question

What are the canonical, agent-neutral roles in the v1 task lifecycle, and
which fields must every role card specify so assignments, fallbacks, inputs,
outputs, authority, and escalation remain unambiguous?

## Comments

- Created while charting **Neutral orchestration templates v1 — decision map**.

## Answer

The v1 canonical role vocabulary is:

- **Owner** — human authority for task objective, budget, mandatory gates, and
  final acceptance.
- **Coordinator** — directs lifecycle, plan, dependencies, limits, and
  escalations without taking Owner authority.
- **Researcher** — produces evidence, constraints, and decision options.
- **Author** — produces non-executable artifacts: briefs, plans,
  specifications, reports, changelogs, and user-facing documentation.
- **Builder** — produces executable or operational artifacts: code,
  configuration, migrations, and infrastructure changes.
- **Reviewer** — independently evaluates artifacts against requirements,
  evidence, risks, and acceptance criteria.
- **Integrator** — composes accepted artifacts, records handoffs/outcomes, and
  prepares the result for Owner acceptance.

One agent may hold multiple roles. A Reviewer must not review its own work for
risk-bearing changes.

Every role card has nine fields: `Mission`; `Responsibilities / Non-goals`;
`Inputs / Outputs`; `Authority`; `Owner gates`; `Acceptance criteria`;
`Default assignment / fallback`; `Limits`; and `Escalation triggers`.
Default-assignment values remain deferred until the subscription model inventory
is recorded. The vocabulary is recorded in `CONTEXT.md`.
