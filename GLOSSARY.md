# Ageroot

Ageroot renders and updates a portable agent-infrastructure stack in a project. This context names its update safety concepts and project-memory responsibilities.

It also defines the portable orchestration vocabulary used by the neutral
orchestration-template specification.

## Language

**Owner**:
The human who owns a task's objective, budget authority, mandatory gates, and
final acceptance.
_Avoid_: sponsor, product owner, requester, approver

**Coordinator**:
The agent role that directs the task lifecycle, maintains its plan,
dependencies, limits, and escalations; it does not acquire the Owner's
authority.
_Avoid_: manager, supervisor

**Researcher**:
The agent role that gathers and evaluates evidence, constraints, and options
for a decision.
_Avoid_: investigator

**Author**:
The agent role that produces non-executable task artifacts, including briefs,
plans, specifications, reports, changelogs, and user-facing documentation.
_Avoid_: planner, documenter

**Builder**:
The agent role that produces executable or operational task artifacts,
including code, configuration, migrations, and infrastructure changes.
_Avoid_: implementer

**Reviewer**:
The agent role that independently evaluates an artifact against requirements,
evidence, risks, and acceptance criteria.
_Avoid_: approver

**Integrator**:
The agent role that composes accepted artifacts, records handoffs and outcomes,
and prepares the result for Owner acceptance.
_Avoid_: release manager

**Orchestration budget**:
The planned and observed resource envelope for one orchestration run, expressed
as iteration count, agent turns, model-capability units, and optionally
wall-clock time.
_Avoid_: price limit, token limit

**Model-capability unit**:
A configurable model-usage unit. It may represent actual token-based provider
cost where usage pricing is available, or a weighted capability proxy where a
subscription does not expose a monetary cost.
_Avoid_: fixed price, token count

**Capability profile**:
A named, provider-agnostic classification of model strengths (`fast`,
`coding`, `reasoning`, `review`) used by role definitions instead of concrete
model identifiers.
_Avoid_: model tier, model tag

**Model inventory**:
A replaceable local registry mapping capability profiles and roles to concrete
subscription or provider models, invocation surfaces, context limits, and
fallback paths.
_Avoid_: model catalog, model list

**Budget warning**:
A Coordinator report raised when any finite orchestration-budget dimension
reaches 80% of its planned limit. Work continues while the Owner receives
plan-versus-actual data, a completion forecast, and a cost-reduction option.
_Avoid_: soft stop, approval gate

**Budget hard gate**:
A mandatory Owner decision raised when any finite orchestration-budget
dimension reaches 100% of its planned limit. No new work iteration or task may
start until the Owner re-baselines the limit, reduces scope, or stops work.
_Avoid_: automatic reset, silent overrun

**Iteration**:
One role attempt to create or materially revise its output in response to
feedback, review, or new evidence. A repeated tool call using the same
strategy is not an iteration; a new approach or artifact version is.
_Avoid_: agent turn, tool retry

**Iteration limit**:
A two-level limit: a run-level allowance plus per-role/per-output limits. The
v1 default is three iterations for one role output and three Builder–Reviewer
rework cycles; the Owner may override either in the plan.
_Avoid_: unlimited polishing, retry cap

**Human gate**:
A paused decision point that requires an Owner choice before the affected task
branch can continue. The Coordinator supplies a decision packet containing
context, options, recommendation, and scope/budget/risk impact; independent
branches may continue within their own limits.
_Avoid_: notification, automatic approval

**Decision packet**:
The structured information sent by the Coordinator to an Owner at a human
gate: context, viable options, recommendation, and projected scope, budget,
and risk impact.
_Avoid_: alert, status update

**Portable orchestration package**:
A self-contained, exact distribution copy of the canonical
`templates/orchestration/v1/` source under a consumer's
`.agents/orchestration/`. It contains templates, manifest, lifecycle map,
schemas, and validation support; it is neither a source link nor a runtime.
_Avoid_: runtime adapter, source reference, generated install artifact

**Portable package synchronization**:
A maintainer-driven source-to-distribution mirror with a non-mutating
`--check` mode that reports drift and an explicit `--write` mode that applies
the copy. Synchronization is never an implicit side effect of editing source.
_Avoid_: automatic overwrite, install-time generation

**Orca orchestration adapter**:
A portable, opt-in adapter that maps a neutral orchestration lifecycle into
Orca Run, Task, Dispatch, worktree, and completion operations. Neutral
templates remain the policy source; Orca supplies supervised execution state.
_Avoid_: replacement lifecycle, implicit Orca mode

**Orca decision task**:
A coordinator-owned Orca Task representing one neutral human gate. It blocks
dependent tasks until the Owner's structured reply is recorded; Coordinator
then applies that decision to the DAG.
_Avoid_: manual status change, out-of-band approval

**Orca implementation worktree**:
The one Orca worktree assigned to an implementation task. Overlapping Builder
writes are serial; parallel write work needs separate child worktrees after
Coordinator path-ownership validation. Reviewer is read-only and branches are
never automatically deleted at final acceptance.
_Avoid_: per-role worktree, automatic branch cleanup

**Orca adapter test modes**:
The adapter defaults to `--dry-run`, which validates and prints the planned
Orca mapping without calls. Explicit `--apply` creates only Run/Task state;
explicit `--execute` permits worktree and Dispatch operations after Owner Start
approval.
_Avoid_: implicit apply, background daemon

**Orca adapter audit trail**:
Portable mapping and decision evidence stored under
`.planning/<plan-id>/orca/`, including `run-map.json` and decision packets.
Orca Run/Task state remains the operational control plane.
_Avoid_: Orca-only history, Markdown-only status

**Orca adapter acceptance scenario**:
A disposable full four-phase lifecycle tested first in `--dry-run` and then
with explicit `--apply` creating only Run/Task/DAG state. Dispatch and
worktree creation require a later explicit `--execute` after Owner Start
approval.
_Avoid_: production first run, implicit agent dispatch

**Phase template**:
A neutral, reusable specification defining participating roles, entry/exit
criteria, handoff artifacts, internal workflow, budget allocation, and
escalation gates for one lifecycle stage.
_Avoid_: step definition, workflow script

**Lifecycle composition map**:
A declarative specification wiring phase templates into an end-to-end task
lifecycle with mandatory Owner human gates and explicit rework loopback rules.
_Avoid_: orchestrator pipeline, workflow graph

**Handoff artifact**:
A typed contract document exchanged across phase boundaries, specifying
required sections, schema assertions, producing role, and consuming role.
_Avoid_: intermediate output, phase dump

**Change request**:
A structured request produced during implementation or integration describing
a discovered deficit, impacted artifacts, and proposed upstream revision.
_Avoid_: bug ticket, rework note

**Safety-first dry-run comparison**:
A strategy-aware pre-apply assessment that distinguishes intended generated changes from local modifications and conflicts before any update can be applied.
_Avoid_: file diff, sync check

**Hybrid baseline**:
The comparison basis that uses current, newly rendered, and prior rendered versions for renderer-owned strategies; external links have no content baseline and are validated separately.
_Avoid_: universal baseline, state-only comparison

**Proposed region merge**:
A deterministic dry-run result for a managed-regions file with intact region markers that preserves declared user regions and replaces only declared generated regions; it warns about local edits and is shown for confirmation before application.
_Avoid_: automatic overwrite, whole-file merge

**Malformed region structure**:
A managed-regions file whose declared region markers are missing, unpaired, moved, or otherwise fail structural validation. It is a blocking conflict because no safe proposed region merge can be calculated.
_Avoid_: mergeable local edit, recoverable marker drift

**Rendered baseline snapshot**:
The complete, separately stored result of an approved render for a renderer-owned file. State references the snapshot and records its SHA-256 for integrity verification.
_Avoid_: inline state content, hash-only baseline

**Unverified comparison**:
A two-way comparison between a current renderer-owned file and its new render when snapshot persistence is disabled. It cannot classify local modifications and is explicitly labelled before confirmation.
_Avoid_: safety-first classification, conflict check

**External-link validation**:
A dry-run check that an external link exists and resolves to its expected target. It reports link state only; Ageroot neither compares target content nor applies changes to it.
_Avoid_: external-link content diff, external-link update

**Snapshot persistence policy**:
An installation-wide configuration setting that enables or disables rendered baseline snapshot storage for every renderer-owned file.
_Avoid_: per-file snapshot policy, per-strategy snapshot policy

**Summary-first confirmation**:
An approval rule under which a concise dry-run summary is sufficient for confirmation, while complete diffs remain available on request.
_Avoid_: mandatory-diff confirmation, diff-free confirmation

**Tiered confirmation summary**:
A concise report that gives counts for changed and unchanged files, and path-level reasons, apply eligibility, and a full-diff access method only for conflicts and blocked files.
_Avoid_: all-path summary, content-in-summary

**Atomic apply**:
An approval outcome that applies the entire update only when every renderer-owned path is eligible. Any conflict or blocked path prevents all managed changes.
_Avoid_: partial apply, per-path confirmation

**Snapshot integrity escalation**:
A required explicit user decision when snapshot persistence is enabled but a baseline snapshot is missing or fails SHA-256 verification. No update is applied automatically.
_Avoid_: silent unverified fallback, automatic baseline replacement

**One-time unverified override**:
An explicit, single-update user approval to use an unverified comparison after snapshot integrity escalation. It does not replace or repair the stored baseline.
_Avoid_: persistent integrity bypass, baseline acceptance

**Transactional snapshot commit**:
The atomic persistence of every new rendered baseline snapshot, its SHA-256, and state only after every managed change has applied successfully.
_Avoid_: per-file snapshot commit, deferred snapshot update

**Update engine**:
The unified module that runs a safety-first dry-run comparison over new renders and executes atomic apply with transactional snapshot commit.
_Avoid_: comparison runner, update script

**Distribution module**:
The module that discovers canonical sources, verifies completeness and ownership, renders the consumer payload mapping, and validates whole-payload drift before handoff to the Update engine.
_Avoid_: package manager, install script, template generator

**Workspace drift check**:
A pre-apply verification that workspace file contents match the hashes observed during dry-run inspection, preventing concurrent file edits from being silently overwritten.
_Avoid_: sync check, optimistic locking

**Deletion escalation**:
A required, separate explicit confirmation for a renderer-owned managed file that is absent from a new render. Its presence blocks the ordinary update flow.
_Avoid_: ordinary update deletion, implicit removal

**Locally modified deletion**:
A proposed deletion whose current file differs from its rendered baseline. It is blocked until the user manually preserves or relocates the file and repeats the dry run.
_Avoid_: confirmed destructive deletion, snapshot backup

**Snapshot store**:
The project-local `.agents/snapshots/` directory that holds rendered baseline snapshots. It is excluded from Git.
_Avoid_: tracked snapshot store, user-home snapshot store

**Unverified migration bootstrap**:
The first dry run for an existing installation with snapshot persistence enabled but no snapshot store. It requires explicit confirmation and creates baseline snapshots only after a successful apply.
_Avoid_: implicit baseline adoption, mandatory manual migration

**Deterministic content normalization**:
Comparison preprocessing that removes line-ending, final-newline, trailing-whitespace, and formatter-only Markdown/YAML noise without changing YAML data, key order, Markdown structure, or text.
_Avoid_: semantic normalization, lossy formatting

**Comparison result class**:
The fixed outcome vocabulary for one managed path: `unchanged`, `changed`, `unverified`, `region-merge`, `conflict`, `blocked`, `invalid-link`, or `deletion-pending`.
_Avoid_: ad-hoc status, ambiguous warning

**Memory workflow**:
Use of project memory while carrying out a task, including retrieval, recording experiences, and explicit review of proposed knowledge. It adds to experience and knowledge histories without replacing existing entries.
_Avoid_: memory maintenance, task planning

**Memory maintenance**:
Work on accumulated project memory outside the active task, including synthesis, archival, cleanup, and search-index upkeep. It may reorganize stored memory but does not automatically accept proposed knowledge.
_Avoid_: memory workflow, automatic knowledge acceptance

**Project preferences**:
User-authored conventions for a specific project, distinct from experiences and knowledge accumulated by agents. They have one authoritative record and are referenced by the agent instructions.
_Avoid_: personal memory, learned preferences

**Agent package**:
A versioned, content-hashed distribution unit containing agent primitives such as skills, instructions, prompts, or tool definitions.
_Avoid_: skill bundle, plugin archive

**APM manifest**:
The declarative project configuration file (`apm.yml`) defining required agent packages, version constraints, and deployment targets.
_Avoid_: package config, skill manifest

**Ageroot management skill**:
The first-party agent skill (`skills/ageroot`) responsible for installing, configuring, verifying, and updating the Ageroot stack and synchronizing APM packages.
_Avoid_: setup script, update runner, install guide

**Skill materialization**:
The automated deployment and layout of resolved agent skills into the authoritative `.agents/skills/` target directory.
_Avoid_: skill copying, manual linking
