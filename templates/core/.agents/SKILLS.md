# Project skills

<!-- generated-by: ageroot; template: <template-version>; commit: <short-git-commit>; rendered-at: <ISO-8601 timestamp> -->

Project skills are managed with [APM (Agent Package Manager)](https://github.com/microsoft/apm).
Dependencies and exact content hashes are tracked in `apm.yml` and `apm.lock.yaml`, deploying directly to `.agents/skills/` via the `agent-skills` target.

## Prerequisites

Install APM before managing skills:

```bash
# macOS via Homebrew
brew install apm

# Unix standalone installer
curl -sSL https://aka.ms/apm-unix | sh
```

Verify installation:
```bash
apm --version
```

## Operating rules

- Use `apm install`, `apm add`, and `apm remove` to manage project skills.
- Do not manually edit files inside `.agents/skills/`; manage them via `apm.yml`.
- Keep `apm.lock.yaml` tracked in Git for byte-for-byte reproducibility; keep `apm_modules/` and `.agents/skills/` ignored.
- Read this file only when configuring or updating skills; it is not required at normal agent startup.
- Keep this list aligned with project needs. Categorization is policy, not an installed-state report.

## Required

- `caveman` — concise communication protocol.
- `rtk` — token-efficient shell command output.

## Recommended

- `caveman-commit` — concise Conventional Commit messages.
- `caveman-explore` — read-only repository orientation and cross-file discovery.
- `caveman-review` — compact code-review findings.
- `planning-with-files` — durable planning for multi-step implementation work.
- `memory-manager` — episodic reflection, append-only journal writes, candidate review, semantic rendering, FTS5 search, and migration.
- `memory-maintenance` — offline clustering, candidate staging, decay/archival, review queue upkeep, and FTS rebuilds (depends on `memory-manager`).

## Optional

### [mattpocock/skills](https://github.com/mattpocock/skills)

Engineering and workflow skills for disciplined agentic development:

- `setup-matt-pocock-skills` — configure repo for engineering skills (issue tracker, triage labels, domain docs).
- `ask-matt` — route to appropriate skill or flow for current situation.
- `grill-me` — relentless interview to stress-test and sharpen plans or designs.
- `grill-with-docs` — design interview that updates domain model, `GLOSSARY.md`, and ADRs.
- `to-spec` — synthesize conversation into formal issue spec.
- `to-tickets` — decompose plans/specs into dependency-linked tracer-bullet tickets.
- `implement` — execute spec/tickets driven by TDD and reviewed before commit.
- `tdd` — test-driven development loop (red-green-refactor).
- `diagnosing-bugs` — structured hypothesis-driven bug and regression diagnosis loop.
- `code-review` — parallel sub-agent review for standards compliance and spec fidelity.
- `codebase-design` — shared vocabulary and patterns for deep module boundaries.
- `improve-codebase-architecture` — scan codebase for architectural deepening opportunities.
- `domain-modeling` — sharpen ubiquitous language and maintain project domain context.
- `resolving-merge-conflicts` — intent-based hunk-by-hunk git conflict resolution.
- `prototype` — build throwaway prototypes to validate logic or UI.
- `research` — investigate questions against primary sources into cited Markdown.
- `triage` — state-machine issue and PR triage workflow.
- `wayfinder` — multi-session project planning via decision ticket maps.
- `wait-what` — re-pitch unclear or mismatched communication.
- `handoff` — compact session context into a structured handoff document.
- `wizard` — interactive bash wizard for human-only operational steps.
- `teach` — stateful instructional workspace for interactive learning.
- `to-questionnaire` — convert open decisions into targeted stakeholder questionnaires.
