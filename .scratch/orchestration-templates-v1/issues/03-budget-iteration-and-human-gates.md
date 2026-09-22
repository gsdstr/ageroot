# Define budget, iteration, and human-gate policy

Type: grilling
Status: resolved
Assignee: /root

## Question

Which budget units and planned-versus-actual thresholds govern an orchestration
run, how are iteration limits counted, and what exact human decision is needed
when a limit or a gate is reached?

## Comments

- Created while charting **Neutral orchestration templates v1 — decision map**.

## Answer

An orchestration budget is composite: iterations, agent turns,
model-capability units, and optional wall-clock time. A model-capability unit
may use actual token-based provider cost where available; otherwise it is a
configured capability weight suitable for subscriptions.

The v1 standard profile is:

| Dimension | Default |
| --- | ---: |
| Run-level iterations | 12 |
| Iterations per role/output | 3 |
| Builder–Reviewer rework cycles | 3 |
| Agent turns | 30 |
| Model-capability units | 100 |
| Wall-clock time | 120 minutes |
| Budget warning / hard gate | 80% / 100% |

An iteration is a role attempt to create or materially revise its output after
feedback, review, or new evidence. Repeated tool calls using the same strategy
do not count; a new approach or artifact version does. Limits exist at both
run and role/output level. The Owner may override any default at the start.

At 80% of any finite budget dimension, the Coordinator warns the Owner with
plan-versus-actual data, completion forecast, and a cost-reduction option.
Work may continue. At 100%, no new iteration or task may start until the Owner
re-baselines the limit, reduces scope, or stops work.

Every human gate uses one decision packet: context, options, recommendation,
and projected scope/budget/risk impact. Gates cover start, plan-to-build,
final integration, conflicts, missing access, irreversible actions, and limit
breaches. The affected branch pauses pending Owner choice; independent branches
may continue within their own limits.
