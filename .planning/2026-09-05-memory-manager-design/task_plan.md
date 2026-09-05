# Task Plan: Memory manager design

## Goal
Reach shared understanding for extracting agentic-stack memory into ageroot_skills/memory-manager as two workflow/maintenance skills and integrating them into ageroot_template with episodic/semantic memory and separate project preferences.

## Next Step
Antigravity owns implementation in the independent Orca worktree; await its handoff separately.

## Current Phase
Phase 5: Full implementation handoff to Antigravity

## Phases
### Phase 1: Discovery
- **Status:** complete
### Phase 2: Decision rounds and glossary
- **Status:** complete
### Phase 3: Publish requested specification and deferred issues
- [x] Create .scratch/memory-skills/spec.md.
- [x] Create separate hooks and maintenance-invocation issues.
- [x] Replace preliminary design with canonical-spec pointer.
- **Status:** complete
### Phase 4: Review implementation mechanics and shared understanding
- [x] Prepare concrete runtime/path/search/concurrency/migration proposals for review.
- [x] Confirm shared understanding before implementation; user accepted Q13/Q14 and changed Q12 to all memory in Git.
- **Status:** complete
### Phase 5: Runtime extraction and implementation
- [x] Prepare the implementation contract and pinned upstream source closure.
- [x] Create an independent Orca worktree and hand off ownership to Antigravity.
- **Status:** complete
### Phase 6: Skill and template integration
- **Status:** pending
### Phase 7: Validation and delivery
- **Status:** pending

## Decisions Made
- Memory categories: episodic/ and semantic/; personal/ removed from the target model (Q4 confirmed).
- User selected grill-with-docs; design confirmation precedes implementation.

- Integration category: Recommended (confirmed by user).
- Scope: full upstream memory runtime, consolidated into two skills for task workflow and off-task maintenance (confirmed by user).
- Project preferences remain .agents/PREFERENCES.md, referenced from AGENTS.md (Q4 confirmed).
- Use upstream runtime behavior: workflow journals append-only; maintenance may rewrite (Q5/Q8 confirmed). Candidate state and derived views may be updated.
- memory-manager: search/read, episode recording, knowledge review and explicit acceptance (Q6 confirmed).
- memory-maintenance: clustering, candidate preparation, cleanup/archival, index maintenance (Q6 confirmed).
- First version uses FTS5; embeddings deferred (Q7 confirmed).

- One runtime copy inside memory-manager, used by memory-maintenance (Q9 confirmed).
- Initial integration uses the portable AGENTS.md protocol; hooks deferred to a local issue (Q10 confirmed).
- Initial maintenance invocation is an explicit command; automatic trigger options deferred to a local issue (Q11 confirmed).
- Canonical spec and two deferred issues belong in .scratch/memory-skills/ (explicit user request).

- All memory, including auxiliary state, stays eligible for Git tracking; no memory-specific ignores (Q12 user correction).
- Bounded lock waiting with explicit timeout failure (Q13 accepted).
- Source-preserving migration with preview/apply in first version (Q14 accepted).
- User confirmed final design for implementation with these answers.

## Errors Encountered
- Skill invocation tool unavailable; read skill files directly.
- GitHub API rate limit during worker runtime research; retain verified facts and leave scheduling details unverified.
