# Task Plan: Orchestration templates wayfinding

## Goal
Produce a buildable v1 specification for neutral orchestration templates covering four named agents and subscription-available models; do not implement a runtime adapter.

## Next Step
Review completed orchestration-template implementation and prepare delivery.

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent
- [x] Identify constraints
- [x] Document in findings.md
- **Status:** complete

### Phase 2: Planning & Structure
- [x] Define approach
- [x] Create project structure
- **Status:** complete

### Phase 3: Specification synthesis
- [x] Collapse resolved Wayfinder decisions into one buildable specification
- [x] Link decisions as primary sources
- **Status:** complete

### Phase 4: Testing & Verification
- [ ] Verify requirements met
- [ ] Document test results
- **Status:** pending

### Phase 5: Delivery
- [ ] Review outputs
- [ ] Deliver to user
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use Wayfinder planning | User explicitly invoked it; requested work exceeds one session and needs unresolved choices tracked. |
| V1 destination | Produce a specification and role maps, not a runnable orchestration system. |
| Representation | Use a neutral format rather than binding the specification to one orchestrator. |
| V1 focus | Cover the end-to-end task lifecycle. |
| Role binding | Roles are agent-neutral; each gets default and fallback agent assignments. |
| Model representation | Use capability profiles plus a local, replaceable model inventory. |
| Template package | Four phase templates plus one composed lifecycle map. |
| Human escalation | Gate on lifecycle transitions, risk conditions, iteration excess, and cost-plan overrun. |
| Role contract | Seven canonical agent-neutral roles and nine role-card fields. |
| Budget and gates | Composite standard budget profile, 80% warning, 100% hard gate, Owner decision packets, and three-iteration/rework defaults. |
| Model inventory & profiles | Core Antigravity (Gemini) and ChatGPT (Codex) subscription models in local model-inventory.md, excluding low-limit Claude options, 7-field schema, 4 capability profiles, two-tier quota fallback. |
| Template package & lifecycle map | 7-field phase template schema across 4 phases, linear composition map with Owner gates, planning-with-files handoffs, Reviewer-blocking conflict rule, protocol docs, and distribution in templates/orchestration/v1/ and ageroot_template/.agents/orchestration/. |
| Default agent & model assignments | Six agent roles bound to Antigravity (gemini-3.8-flash-high, gemini-3.1-pro-high) and Codex (gpt-5.6-sol, gpt-5.6-terra, gpt-6-astra, codex-auto-review); orthogonal Builder/Reviewer rule enforced; Hermes/Pi set as Tier-3 emergency fallbacks with Owner decision packets. |
| Specification | Synthesized `.scratch/orchestration-templates-v1/spec.md`; map is resolved and ready for ticketing. |
| Implementation tickets | Four dependency-ordered, agent-ready tickets cover schema scaffold, templates, protocol alignment, and validation. |
| Schema scaffold | Implemented `templates/orchestration/v1/` manifest, schemas, offline validator, and tests; ticket 06 resolved. |
| Phase templates and lifecycle | Implemented and validated four phase templates, lifecycle map, handoffs, loopbacks, and budget slices; ticket 07 resolved. |
| Portable protocol alignment | Aligned template protocol and delegation matrix; created ticket 10 for the still-missing portable package distribution. |
| Portable distribution | Implemented explicit sync check/write and mirrored the self-contained package without development tests; ticket 10 resolved. |
| Package validation | Implemented source/portable offline checks and nine negative/positive tests; ticket 09 resolved. |

## Errors Encountered
| Error | Resolution |
|-------|------------|
| Initial planning-skill path was wrong | Located it at `.agents/skills/planning-with-files/`; no work lost. |
| Broad spec patch did not match current plan | Re-read planning files after concurrent updates and applied narrow patches. |
| First ticket patch was malformed | Corrected the missing addition marker; no file was changed by the failed patch. |
