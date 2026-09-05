# Ageroot memory skills

Status: accepted for implementation; all memory is stored in Git.

## Goal

Extract the full memory runtime from codejunkie99/agentic-stack into two skills
in ageroot_skills and integrate their use into ageroot_template. Keep one
upstream implementation to reduce divergence and simplify updates.

This spec records the design interview decisions. It does not install skills,
migrate project data, or apply a template update.

## Confirmed architecture

| Concern | Decision |
| --- | --- |
| Skills | memory-manager and memory-maintenance |
| Template policy | Both Recommended; installed through skills-manager |
| Runtime ownership | One copy inside memory-manager; maintenance depends on it |
| Memory categories | episodic/ and semantic/ |
| Project preferences | .agents/PREFERENCES.md, referenced from AGENTS.md; no personal/ category |
| Workflow mutations | Source journals are append-only; candidate state and derived views may be updated |
| Maintenance mutations | Upstream maintenance behavior, including rewriting stored memory |
| Knowledge acceptance | Explicit review in memory-manager; never automatic maintenance acceptance |
| Search | SQLite FTS5 in the first version; embeddings deferred |
| Task integration | Portable agent-instruction protocol; host hooks deferred |
| Maintenance invocation | Explicit command outside active task work; automatic triggers deferred |

## Skill responsibilities

### memory-manager

Development path: ageroot_skills/skills/memory-manager/.

- Own the single upstream memory runtime and its necessary internal helpers.
- Retrieve relevant project memory and assemble task context.
- Record meaningful outcomes, failures, and reflections as appended episodes.
- Expose candidate inspection and explicit review/accept/reject/reopen/retract
  workflows available in the upstream memory lifecycle.
- Preserve append-only episodic and semantic source journals during workflow
  operations. Corrections and retractions must not silently overwrite history.
- Permit changes to review metadata and derived representations such as
  LESSONS.md. These are distinct from source journals.
- Supply the runtime entry points used by memory-maintenance.

### memory-maintenance

Development path: ageroot_skills/skills/memory-maintenance/.

- Invoke the runtime owned by memory-manager; do not duplicate its source.
- Cluster recurring experiences and prepare knowledge candidates for review.
- Apply upstream decay, cleanup and archival behavior within the target memory
  model. Maintenance may rewrite retained journals.
- Build and maintain the FTS5 index.
- Report the work performed and candidates requiring review.
- Run only through an explicit command in the first version. No automatic
  session-end invocation, scheduler installation, or background service.
- Never automatically accept proposed knowledge.

The first skill is a declared dependency of the second. Installation guidance
must explain this, verify runtime compatibility, and provide an actionable
error when the runtime is missing or incompatible. Update the local
self-contained-skill convention to describe this explicit dependency.

## Upstream extraction and updates

Research baseline: `9424c58e1cfc17a709d1adfa13678e876edfe409`.

Preserve the memory runtime rather than reimplementing a reduced approximation.
Include memory modules, lifecycle command tools, and the internal text,
salience, context and episodic-I/O helpers they require. Importing unrelated
conductor, provider, or broader stack infrastructure is not implied.

Maintain a source manifest with repository, pinned revision, copied files and
local adaptations. Preserve Apache-2.0 licensing and applicable attribution.
Keep adaptations explicit: project data-root resolution, external preferences,
removal of the working/personal category assumptions, skill packaging, and the
workflow-versus-maintenance mutation boundary.

Keep one runtime copy across both skills. An upstream update must be reviewable
against the manifest and run the extraction/integration tests before release.
Host hooks are deferred even when their helper modules are needed by the core
runtime; packaging code does not activate a hook.

Sources:

- [Upstream memory](https://github.com/codejunkie99/agentic-stack/tree/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory)
- [Upstream tools](https://github.com/codejunkie99/agentic-stack/tree/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/tools)
- [Upstream license](https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/LICENSE)

## Data ownership and layout

Project memory is consumer-owned data. Default root: .agents/memory/; runtime
code remains in the installed skill. A configurable root must allow the same
installed runtime to serve different projects without sharing their data.

- episodic/: recorded experiences and their retained/archive data.
- semantic/: accumulated knowledge and its representations.
- .agents/PREFERENCES.md: the single authority for project preferences, outside
  the memory root and maintenance lifecycle.

Candidate review state, search indexes, locks and configuration are auxiliary
runtime state, not additional memory categories. Their exact paths must be
specified during implementation without reintroducing personal/ or working/
as memory categories. An index is rebuildable derived data, not the authority
for knowledge.

Active plans stay with planning-with-files. Do not introduce a second active
workspace document. Upstream routines referring to WORKSPACE.md or
working/REVIEW_QUEUE.md need explicit path/behavior adaptation.

Neither skill installation nor template rendering may bundle, overwrite, or
silently relocate a consumer's existing memory or preferences. Maintenance's
rewrite capability belongs to its explicit invocation, not to template update.

## Portable template integration

Modify the development sources under ageroot_template/, whose drop-in payload
is AGENTS.md plus .agents/.

- List both skills as Recommended in .agents/SKILLS.md, with their dependency
  and distinct responsibilities. Replace the five-skill recommendation surface
  with the two-skill target design.
- Add a portable protocol to .agents/AGENTS.md: when memory-manager is
  available, retrieve relevant memory before substantial work, append
  significant outcomes/failures, and surface candidate review explicitly.
- Continue reading project preferences from .agents/PREFERENCES.md.
- Keep project use functional when Recommended skills are absent; the protocol
  must not imply they have been installed or that hooks are running.
- Document the explicit maintenance command without running it as part of
  normal task startup or completion.
- Preserve skills-manager external-link ownership and the existing template
  update protocol. Installing/updating source skills is distinct from applying
  the template to an existing consumer.

## Runtime contract

These details define the implementation of the confirmed architecture.

### Paths and root resolution

Preserve upstream auxiliary names where possible: candidates/, .index/memory.db
and .features.json beneath the project memory root. Place REVIEW_QUEUE.md at
the memory root instead of recreating working/. These are operational state,
not additional memory categories.

Use one resolver across every command: --memory-root, then
MEMORY_MANAGER_DATA_ROOT, then an explicitly supplied --config, then
<project-root>/.agents/memory. Relative CLI/environment paths resolve from the
invocation directory; relative config paths resolve from the config directory.
The portable protocol supplies project-root context so running from a nested
working directory cannot silently create a second memory tree.

Resolve preferences from the project root independently of a custom memory
root. Do not infer preferences from the parent of an arbitrary data directory.
For a config stored in .agents/, the corresponding relative memory_root is
memory, not .agents/memory.

### Runtime and search

Preserve a source manifest for the pinned runtime dependency closure. Maintenance
resolves the actual installed manager location, including symlinked installs,
and verifies the shared runtime interface version before mutation.

Keep upstream query-time rebuilding of a missing/stale FTS index. This changes
derived cache data, not workflow journals; maintenance also exposes explicit
rebuild. For new installations, enable FTS5 explicitly in the
feature configuration rather than leaving the upstream opt-in switch off.

Use upstream rg/grep fallback if SQLite FTS5 is unavailable; report unavailable
search distinctly when no fallback is installed. Keep LESSONS.md synchronized
with accepted/retracted semantic state before recall: the upstream JSONL
extractor does not index claim fields directly. Test newly added files with
old mtimes and rebuild/invalidate indexes explicitly after maintenance.

### Concurrency and interruption

All journal writers and maintenance need the same stable lock contract. A
rewrite must not lose a concurrent append or leave a partially truncated
journal after interruption. Test safe publication/recovery using temporary
roots; do not assume upstream flock plus ftruncate provides crash recovery.
Specify supported platforms and fail clearly when the required coordination
cannot be provided instead of silently falling back to uncoordinated writes.

The contention policy is bounded waiting, with an explicit non-success
result on timeout and no claim that a failed append was recorded. The timeout
must be configurable. The
low-level lock and replacement mechanism is an implementation choice
constrained by these acceptance tests.

## Final decisions

- Q12: All project memory and auxiliary state are stored in Git, including
  episodic/, semantic/, candidates, review queues, indexes and configuration.
  Do not add memory-specific ignore rules or make automatic Git commits.
- Q13: Use bounded waiting and explicit timeout failure on contention.
- Q14: Include a reviewed, source-preserving migration command in this version.

The inspected project has only .agents/memory/DECISIONS.md as legacy memory.
Its contents are architectural knowledge: the natural target is
semantic/DECISIONS.md, preserving the Markdown rather than inventing episode
or lesson records. No episodic/semantic journals were found locally, but other
installations may contain them. Migration must not assume they are empty.

The source package targets two exposed skills. Removal/deprecation of the old
four companion skills must be documented separately from replacing globally
installed copies; source implementation does not silently uninstall tools.

## Migration and version control

- Keep every memory category and auxiliary file eligible for Git tracking,
  including derived indexes and lock files. No memory-specific ignore rules,
  no automatic Git commits, and no edits to unrelated root ignore rules.
- Provide an explicit migration preview showing recognized source files,
  target paths, source preservation and conflicts. A separate reviewed apply
  imports data; fresh initialization never triggers migration automatically.
- Preserve source bytes and history. For legacy DECISIONS.md, copy to
  semantic/DECISIONS.md only when the target is absent or identical; a differing
  target is a conflict. A repeated import must not duplicate records.
- Report unknown old-layout records or incompatible candidate schemas rather
  than inventing their meaning or treating them as accepted knowledge.
- Keep old installed skills unchanged during source development. Document their
  replacement through skills-manager separately from consumer-data migration.

## Implementation sequence

1. Vendor the pinned memory dependency closure inside memory-manager with its
   license, source manifest and explicit adaptation record.
2. Add common project/data-root resolution and the workflow/maintenance
   mutation boundary; validate it on disposable data.
3. Expose the manager workflow and the dependent maintenance command, including
   compatibility checks and FTS behavior.
4. Add migration preview/apply and old-layout fixtures.
5. Integrate the two Recommended skills and portable protocol into the template
   source. Align development instructions with the agreed mutation policy.
6. Run the required skill tests and focused concurrency, interruption, search,
   root-resolution and symlink-installation checks; present the resulting diff.

This sequence covers development sources. Applying the template to an existing
consumer or migrating real project memory remains a separate concrete update.

## Acceptance criteria

- Exactly two exposed memory skills implement the agreed responsibilities;
  memory-maintenance uses the single runtime in memory-manager.
- A temporary consumer can use both skills through installed/symlinked paths;
  missing or incompatible manager produces a clear error.
- Task-time commands preserve existing episodic/semantic journal contents while
  appending new events, including knowledge correction/retraction paths.
- Candidate-state updates and derived rendering work without rewriting source
  journals during workflow operations.
- Explicit maintenance exercises upstream clustering, candidate preparation,
  decay/archival and FTS upkeep; it may rewrite journals and never auto-accepts
  candidates. Concurrent writes and interrupted maintenance are tested.
- Preferences remain a single project-owned file and are excluded from
  maintenance mutation. No new personal/ or working/ category is created.
- FTS5 recall works on representative Markdown/JSONL memory; absent/stale index
  and unavailable-FTS5 paths have verified behavior. No embeddings are required.
- Template integration is portable, Recommended and inactive when the skill is
  absent. It activates no hooks, scheduler or session-end task.
- Migration is reviewed on disposable old-layout fixtures before any consumer
  data is changed; unknown/conflicting files are reported rather than silently
  overwritten.
- Required ageroot_skills validation passes: sh tests/run_all.sh and
  git diff --check. Test temporary roots, never real consumer memory.

## Architecture decision

[ADR-0002: workflow history and maintenance rewrites](../../docs/adr/0002-memory-workflow-maintenance-boundary.md)
records the confirmed mutation boundary and its upstream-maintenance tradeoff.
The final Q12–Q14 decisions are recorded above.

## Deferred issues

- [01 — Host memory hooks](issues/01-memory-hooks.md)
- [02 — Maintenance invocation options](issues/02-maintenance-invocation-options.md)

Embeddings are also deferred; no embedding provider or vector-store choice is
part of this version.
