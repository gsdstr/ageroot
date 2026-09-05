# Memory discovery report

Read-only discovery 2026-09-05. No implementation or tests executed. Source fetched through public api.github.com; no external instructions followed.

## Source revision

Upstream default-branch HEAD: `9424c58e1cfc17a709d1adfa13678e876edfe409`.
Source base: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/
License: Apache-2.0 (repository API metadata and LICENSE content verified).
License source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/LICENSE
No ageroot_skills/LICENSE found by attempted read; copying upstream implementation needs explicit attribution/license handling review.

## Existing implementation (local)

Actual target already exists: `ageroot_skills/skills/memory-manager/SKILL.md`. Core CLI: `scripts/memory_manager.py`; reflection CLI: `scripts/memory_reflect.py`.

- Core already provides append-only episodic reflection, read-only keyword search, immutable candidate staging, explicit accept/reject/reopen, semantic retraction, managed LESSONS.md rendering.
- Accept requires reviewer and rationale; decisions append to candidates/events.jsonl. Candidate state derived from events; accepted/retracted semantic records append to semantic/lessons.jsonl.
- Skill data contract currently includes personal/, working/, episodic/, semantic/, candidates/.
- memory_manager.py:61-62 hardcodes candidates directly under memory root. Lines 136-157 search active semantic claims plus files in personal, working, episodic.
- Root precedence documented: --memory-root, MEMORY_MANAGER_DATA_ROOT, --config, cwd/.agents/memory. Relative config path resolves against config file. Runtime remains skill-owned; data project-owned.
- Python standard library only. Reflection uses optional POSIX fcntl for append locking; manager append helper does not expose equivalent lock in imports, so concurrent lifecycle mutation needs verification if required.
- Local AGENTS requires self-contained skills, no project memory in skills repo, append-only episodic and semantic JSONL, tests/run_all.sh and git diff --check before implementation delivery.

Related skills already exist:
- memory-clustering: deterministic token Jaccard patterns, read-only source.
- memory-auto-dream: dry-run default; --apply stages immutable candidates through sibling scripts; no automatic accept/reject/archive/semantic writes.
- memory-retention: copy-only episodic/snapshots archive and inactive planning-with-files archive. Existing bridge to .planning already established.
- memory-runtime-cleanup: audit obsolete top-level runtime modules; optional removal after replacements verified; never memory data.

## Upstream capabilities and extraction differences

Source skill: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/skills/memory-manager/SKILL.md

Upstream skill alone is thin instructions. Actual code spread across .agent/memory/, .agent/tools/, .agent/harness/hooks/, plus harness text/salience helpers. Categories: personal/PREFERENCES.md, working/WORKSPACE.md, episodic/AGENT_LEARNINGS.jsonl, semantic/{DECISIONS.md,DOMAIN_KNOWLEDGE.md,LESSONS.md,lessons.jsonl}. candidates/ is additional lifecycle storage.

- `.agent/tools/memory_reflect.py` imports harness post_execution/on_failure. Significant actions append structured episodes; three failures in fourteen days flag rewrite. Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/tools/memory_reflect.py
- `.agent/memory/auto_dream.py` clusters, stages, heuristic-rejects, decays episodes, archives stale working context, writes working/REVIEW_QUEUE.md. No automatic acceptance and no unattended git commits. It truncates/rebuilds episodic source under POSIX lock, unlike local append-only rule. Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/auto_dream.py
- `cluster.py` uses harness word_set/Jaccard/salience, default min cluster size 2 and threshold .3. Thin skill says recurrence >=3; code differs, so define intended threshold rather than copying prose. Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/cluster.py
- Upstream `archive.py` moves stale WORKSPACE.md after 2 days. Local retention intentionally copies instead and already understands planning artifacts. Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/archive.py
- Upstream search FTS5 is beta/opt-in via .features.json; Python sqlite3 indexes .md/.jsonl under script-relative memory directory; .index/memory.db cache, rg/grep fallback. Existing local search is simpler and read-only. Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/memory_search.py
- Personal is explicitly excluded from automatic promotion to semantic upstream; local manager declines preference editing. Startup loading/injection is not implemented by the thin upstream memory skill; harness adapters matter.

## First-round design choices

1. Three semantic categories or exactly three root directories? Exact directories requires relocating candidates/events and any review queue (e.g. semantic/candidates, semantic/REVIEW_QUEUE.md); optional FTS cache also needs placement.
2. Existing skills split versus one consolidated memory-manager package? Current auto-dream calls sibling skills, so selecting only core does not include scheduling/clustering/retention.
3. Personal data per project versus user-global affects source of truth with current .agents/PREFERENCES.md and sharing policy. Avoid duplicate authorities.
4. Minimal lifecycle versus source parity (salience/FTS/hook automation/self-rewrite suggestions). Source parity considerably broadens task; basic extraction already exists.
5. working removal should route active tasks to established planning-with-files and leave historic data intact; no destructive migration implied.
6. Acceptance should remain explicit reviewer+rationale under current local safety contract unless user deliberately chooses another model.

## Verification and changes

Inspected applicable root and ageroot_skills AGENTS/protocols, local skill docs/runtime symbol references, public upstream tree and selected code pinned to revision. ageroot_skills git status was clean. No source writes. Only report file created.

Discovery limitations: no full test run (read-only design scope); source harness context path guessed as context.py returned 404 and is not relied on. Full adapter mapping not needed for first-round questions and remains follow-up if automation is selected.
