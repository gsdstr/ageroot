# Specify neutral template package and lifecycle composition map

Type: grilling
Status: resolved
Assignee: /root
Blocked by: 01, 03, 04

## Question

How should the four phase templates and their end-to-end composition map be
structured in a neutral, reusable specification so required handoffs,
artifacts, gates, budgets, and role assignments can be validated without a
runtime adapter?

## Comments

- Created while charting **Neutral orchestration templates v1 — decision map**.

## Answer

The neutral orchestration template package and lifecycle composition map are structured as follows:

1. **Package Layout & Canonical Locations**:
   - Primary reference and template distribution paths:
     - `templates/orchestration/v1/`
     - `ageroot_template/.agents/orchestration/`
   - Directory contents:
     - `manifest.yaml` — Package metadata, version (`1.0.0`), declared templates, and schema bindings.
     - `phases/01-intake.md` — Intake phase template (Owner + Coordinator).
     - `phases/02-research-planning.md` — Planning phase template (Coordinator + Researcher + Author).
     - `phases/03-implementation.md` — Implementation phase template (Coordinator + Builder + Reviewer).
     - `phases/04-review-integration.md` — Integration phase template (Coordinator + Integrator + Reviewer).
     - `lifecycle-map.md` — End-to-end task lifecycle composition map, gates, and loopback rules.
     - `schemas/` — JSON Schemas validating template frontmatter, lifecycle map, and handoff contracts.
   - Reference protocols:
     - `ageroot_template/.agents/protocols/orchestration.md` — Portable orchestration protocol documenting 7 roles, budget policy, human gates, and phase composition.
     - `ageroot_template/.agents/protocols/delegation.md` — Updated delegation matrix linking neutral orchestration.

2. **Phase Template Contract Schema (7 Core Fields)**:
   Every phase template is a Markdown document with YAML frontmatter specifying:
   - `metadata`: `id`, `phase_index` (1-4), `name`, `summary`.
   - `participating_roles`: Declared subset of canonical roles (`Owner`, `Coordinator`, `Researcher`, `Author`, `Builder`, `Reviewer`, `Integrator`).
   - `entry_criteria`: Required inputs, prerequisite artifacts, and entry gates (e.g. Owner Start Gate, Plan-to-Build Gate).
   - `exit_criteria`: Expected deliverables, verification conditions, and required role sign-offs.
   - `handoff_artifacts`: Input and output artifact specifications (schema, producer role, consumer role).
   - `budget_slice`: Recommended allocation of run iterations, agent turns, and model-capability units from the standard budget profile.
   - `escalation_gates`: Phase-specific Human Gate triggers and decision packet templates.

3. **Lifecycle Composition Map**:
   - Linear progression: `01-intake` → `02-research-planning` → `03-implementation` → `04-review-integration`.
   - Mandatory Owner Human Gates:
     - *Start Gate*: Authorizes task objective, scope, and budget profile.
     - *Plan-to-Build Gate*: Evaluates and approves plan/spec before implementation starts.
     - *Final Acceptance Gate*: Evaluates integrated release packet and signs off on completion.
   - Two-tier loopback mechanism:
     - *Autonomous loopback*: Minor defects or revisions within remaining budget envelope loop back upstream (e.g. Implementation → Planning for spec refinement), counted against phase iteration limits.
     - *Escalation loopback*: Breaking architectural shifts, scope increases, or budget/iteration limit breaches trigger a Coordinator-authored Decision Packet at an Owner Human Gate.

4. **Compatibility with `planning-with-files` & Handoff Artifacts**:
   Handoff artifacts directly map to and populate the persistent planning files under `.planning/<plan-id>/`:
   - `task_brief.md` (Phase 1 → Phase 2): Produced by Owner + Coordinator; seeds `.planning/<plan-id>/task_plan.md` (goals, budget limits).
   - `task_spec.md` (Phase 2 → Phase 3): Produced by Author + Researcher; populates `task_plan.md` phases and links findings from `findings.md`.
   - `implementation_manifest.md` (Phase 3 → Phase 4): Produced by Builder + Reviewer; records worker reports (`workers/<task-id>.md`), diff summaries, and test execution in `progress.md`.
   - `release_packet.md` (Phase 4 → Owner): Produced by Integrator + Reviewer; records composed output, regression verification log, and acceptance criteria audit in `progress.md`.
   - `change_request.md`: Structured artifact produced during loopbacks describing the deficit, impacted files, and proposed change.

5. **Conflict Arbitration Rule**:
   - An independent Reviewer holds blocking authority on quality/correctness; Builder iterates up to 3 cycles.
   - If unresolved at the rework cycle limit, Coordinator pauses the affected branch, prepares an Owner Decision Packet (with Builder argument, Reviewer critique, and impact analysis), and escalates to an Owner Human Gate. Coordinator never overrides a Reviewer.

6. **Validation Without Runtime**:
   - Standalone validation via JSON Schema against YAML frontmatter and Markdown headings. Validates that all phases have valid role references, valid budget slices, matching input/output handoff edges, and declared Owner gates without requiring an execution engine.
