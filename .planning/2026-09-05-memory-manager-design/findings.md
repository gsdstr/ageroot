# Findings & Decisions

## Requirements
- Extract memory system from https://github.com/codejunkie99/agentic-stack.
- Target skill: ageroot_skills/memory-manager; integration: ageroot_template.
- Keep episodic/, semantic/, personal/.

## Research Findings
- Existing unrelated working-tree changes: .gitignore and removed ageroot_core files; preserve them.
- Previous comparison-strategy plan has completed handoff; keep its files unchanged.

## Open Decisions
- Memory scope, lifecycle, integration boundary and migration.

## Template findings
- Drop-in payload consists of root AGENTS.md and .agents/ only.
- Skills use external-link ownership; skills-manager installs shared links, template does not copy skill implementation.
- Template startup already has planning-with-files integration and PREFERENCES.md for stable user conventions.
- Memory-manager is currently optional alongside four separate memory companion skills; no tracked memory tree found in template.
- memory-manager actual source location is ageroot_skills/skills/memory-manager.

## Initial source discovery (worker; report pending)
- Existing skill already implements append-only episodic/semantic lifecycle and explicit candidate review using Python stdlib.
- Existing layout also contains working/ and candidates/; search reads working/.
- Upstream identified at 9424c58e1cfc17a709d1adfa13678e876edfe409, Apache-2.0, with runtime beyond SKILL.md tied to .agent/harness.

## Interview frontier
- Q1: project-local memory versus shared personal memory.
- Q2: required versus recommended/optional template integration.
- User answers pending; recommendations are not accepted decisions.
- Q3: portable executable skill versus instructions-only versus full upstream runtime.
- PREFERENCES.md versus personal/ semantics depends on chosen memory scope; lifecycle, migration and ownership details follow Q1–Q3.

## Round 1 answers
- Q1: personal currently only contains project PREFERENCES.md; user asks whether a category is worthwhile. Recommendation: retain separate .agents/PREFERENCES.md referenced by AGENTS.md, exclude it from accumulated-memory lifecycle. Pending acceptance.
- Q2: Recommended, not required.
- Q3: full upstream runtime for maintenance simplicity, consolidated into TWO skills: workflow and off-task maintenance/cleanup/embedding.
- User intent supersedes earlier minimal-runtime recommendation. Full-runtime packaging and any upstream divergences remain open.
- Local extraction AUDIT.md explicitly records deliberate divergence: manual review, copy-only retention and no index DB. Thus new scope reopens existing design choices.
- Q4–Q6 asked: preferences location/category, upstream fidelity versus append-only adaptation, functional split/review boundary.
- Source report: workers/memory_facts.md. Follow-up report requested: workers/runtime_scope.md.

## Runtime follow-up findings
- Worker inspected upstream memory/harness/tools: FTS5 and lexical Jaccard found; no embedding runtime in inspected paths. Upstream semantic DECISIONS lists vector store as rejected.
- Full extraction spans memory modules, memory CLI tools, harness text/salience/context-budget helpers and lifecycle hooks.
- GitHub API rate limit prevented completion of adapter/scheduling inspection; exact scheduling support remains unverified.
- Q7 asked: FTS5 first, embeddings deferred versus actual embeddings required in first version.

## Round 2 answers (confirmed)
- Q4 yes: external .agents/PREFERENCES.md referenced by AGENTS.md; episodic/semantic are the two memory categories.
- Q5 upstream version/behavior; working skill append-only, maintenance may rewrite. This explicitly revises the earlier repository-wide no-rewrite contract for maintenance.
- Q6 yes: memory-manager handles working-task retrieval/recording/review; memory-maintenance handles clustering/staging/cleanup/index maintenance. Acceptance remains explicit in manager.
- Q7 FTS5 initially, no embedding implementation in first version.

## Remaining design edges
- Append-only for source histories versus every file: candidate review state, LESSONS projection and FTS index may be mutable even when histories are append-only.
- Distribution: two self-contained skills versus one shared upstream runtime owner.
- Invocation: task-time protocol/hook coverage and maintenance manual versus host-end versus scheduled.
- Legacy migration and technical directories/cache placement.

## Third-round local facts and questions
- ageroot_skills is an independent nested Git repository.
- Existing auto-dream already invokes sibling scripts, with explicit path overrides. A single runtime owner is feasible, but self-contained skill policy must be reconciled with a declared dependency.
- Current project legacy memory consists of .agents/memory/DECISIONS.md only; no category directories discovered. No memory data tree in template.
- Five old memory skills exist in the shared store; no project-local memory skill links were found. Installed-skill replacement remains implementation work, not an implicit side effect of design.
- Q8–Q11 asked: append-only scope, runtime packaging, task integration/hook scope, maintenance invocation.
- Confirmed decisions and remaining questions consolidated in docs/design/memory-skills.md.

## Round 3 answers (confirmed)
- Q8: source journals append-only; the proposed mutable candidate state/derived-view distinction accepted.
- Q9: one runtime inside memory-manager.
- Q10: portable protocol; user requested a .scratch memory spec and a hooks issue.
- Q11: explicit command; user requested an issue comparing maintenance invocation options.
- Tracker convention: per-feature spec.md plus numbered issue files; canonical Status strings from docs/agents/triage-labels.md.
- Published .scratch/memory-skills/spec.md with confirmed architecture, acceptance criteria and explicitly outstanding implementation mechanics.
- Created issues/01-memory-hooks.md (task, needs-triage) and issues/02-maintenance-invocation-options.md (research, needs-triage).
- docs/design/memory-skills.md is now a pointer to the canonical spec, avoiding divergent design copies.
- No ADR created: final implementation details and full shared-understanding review remain open.

## Continued design review
- User requested continuation after spec/issue delivery. Continue the active design interview before implementing.
- Q12–Q14 asked: Git policy, bounded lock waiting versus fail-fast maintenance, and migration scope. No answers assumed.
- Local gitignore files do not define the target memory-category tracking policy.
- Current core accepts --memory-root, MEMORY_MANAGER_DATA_ROOT and --config; reflect lacks --config. A unified resolver is required for consistent roots.
- Worker found upstream FTS indexes selected episode fields but not semantic claim fields directly; current lessons projection is important for recall.
- Upstream index freshness checks do not detect every newly added file with old mtime; implementation needs coverage of that case.

## Concrete runtime proposal
- Source worker report: workers/final_contract_facts.md. Upstream search lazily rebuilds derived indexes; preserving this is compatible with Q8 journal-only append-only.
- FTS is upstream opt-in. Proposed new-install configuration explicitly enables it; this remains visible for final review, not an earlier confirmed user answer.
- Spec now proposes auxiliary paths, unified resolver, independent preference resolution, lazy index rebuild/fallback and crash-safety acceptance constraints.
- Current DECISIONS.md is semantic architectural knowledge; natural migration preserves Markdown to semantic/DECISIONS.md, pending Q14 scope.
- The final open user frontier is Q12–Q14; low-level manifest/lock details remain implementation work under specified constraints.

## Final review packet
- User said continue again without choosing Q12–Q14. Continued authorized documentation work; no unanswered recommendation was treated as accepted.
- Spec now includes proposed Git/lock/migration defaults and a concrete implementation sequence.
- Created ADR-0002 for the already confirmed workflow-versus-maintenance mutation boundary. It meets ADR criteria: history-retention effects are costly to reverse, different mutation rules are non-obvious, and upstream fidelity versus blanket append-only was an explicit tradeoff.
- Q12–Q14 and final shared-understanding confirmation remain pending.

## Final review answers
- All memory in Git, superseding semantic-only recommendation; include episode/candidate/index/auxiliary state and no automatic commits.
- Bounded lock wait and source-preserving migration accepted. Final design confirmed; implementation now authorized.
- skills and template nested repositories both clean before implementation.
