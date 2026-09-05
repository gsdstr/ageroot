# Full-runtime scope — second round

Revision: `9424c58e1cfc17a709d1adfa13678e876edfe409` (same as first report). Read-only public GitHub API inspection. Source links below reference exact revision. No implementation or dependency installation.

## Meaning of full memory runtime

Preserve upstream memory workflows and interfaces, not just its thin memory-manager instructions. Minimal dependency closure visible from imports:

| Area | Upstream files / dependencies |
| --- | --- |
| Write experiences | tools/memory_reflect.py -> harness/hooks/post_execution.py, on_failure.py -> _provenance.py, _episodic_io.py |
| Recall/context | tools/recall.py -> harness/text.py + memory/render_lessons.py; harness/context_budget.py -> harness/text.py + salience.py; tools/budget_tracker.py -> context_budget |
| Direct learning | tools/learn.py -> harness/text.py + memory/cluster.py; command can stop at candidate staging before graduate |
| Human/host-agent review | tools/list_candidates.py, graduate.py, reject.py, reopen.py, retract_lesson.py; memory/review_state.py, validate.py, render_lessons.py. Imports verified for first four, retract file exists but body request rate-limited |
| Maintenance | memory/auto_dream.py -> promote.py, validate.py, review_state.py, decay.py, archive.py; promote -> cluster + review_state + validate; cluster/validate/decay -> harness/text and/or salience |
| Keyword index | memory/memory_search.py, Python sqlite3 FTS5; fallback rg or grep |
| Harness logging adapters | harness/hooks/claude_code_post_tool.py; copilot_cli_post_tool.py and pi_post_tool.py reuse Claude classifier plus common log/failure functions |

`tools/show.py` exists; body not verified because API rate limit. `harness/conductor.py`, `harness/llm.py`, pre_tool_call permissions, skill_loader, data exports, brain_bridge are broader stack infrastructure rather than established dependencies of inspected memory lifecycle code. Do not include every .agent file under the label full memory runtime without explicit need. All inspected memory imports are standard library plus internal helpers; full stack requirements.txt was rate-limited, so no assertion about whole-stack dependencies.

Source directory references:
- https://github.com/codejunkie99/agentic-stack/tree/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory
- https://github.com/codejunkie99/agentic-stack/tree/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/tools
- https://github.com/codejunkie99/agentic-stack/tree/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/harness

## Embeddings are a new feature, not an extraction fact

Inspected memory modules, harness modules, tools imports and repository tree show keyword retrieval and token Jaccard similarity, not an embedding producer or vector database. Upstream semantic/DECISIONS.md:15 lists vector store among rejected alternatives. This is source design context, not authoritative instruction for our implementation.

FTS5 tokenization, ranking and index rebuild are lexical search. Index lives in memory/.index/memory.db and opt-in flag in memory/.features.json. It is not semantic vector embedding. Adding embedding provider, model, storage, invalidation and privacy decisions expands scope beyond pinned upstream.

Sources:
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/memory_search.py
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/cluster.py
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/semantic/DECISIONS.md

## Workflow versus maintenance boundary

Proposal (inference, not upstream contract): first skill owns context retrieval, reflect, direct learn, candidate review and user-facing lifecycle commands; second owns unattended cluster/stage, archive/decay and index rebuild. Only two skills need be exposed, while shared runtime remains one versioned dependency rather than copied between skills. Runtime ownership/distribution needs a concrete decision because local skill AGENTS says each skill self-contained.

Upstream auto_dream run_dream_cycle loads episodes, clusters patterns, filters salience >=7, stages, rejects obvious junk, archives low-salience older episodes and stale working context, emits review queue. It explicitly does not promote or make git commits. Maintenance automatic acceptance would be a product change.

Logging hooks exist for Claude Code, Copilot CLI and Pi. Source auto_dream comments reference shutdown-hook context and POSIX locking; exact scheduler wiring/adapters not verified because API rate limit. Do not promise portable background maintenance from these facts. A skill does not itself provide a persistent scheduler; adapters must invoke its maintenance entry point. Distinguish a manual command, host session-end hook and actual scheduled service in next design question.

## Preferences: one authority sufficient

Upstream `.agent/AGENTS.md`:8 points directly to memory/personal/PREFERENCES.md as stable user conventions. `harness/context_budget.py`:139-147 always loads this same file alongside AGENTS, working context/review queue and DECISIONS. No second preferences copy required by inspected upstream code.

Local Ageroot currently points to .agents/PREFERENCES.md. Integration can route loader/instruction reference to personal/PREFERENCES.md, or make memory runtime resolve configured existing authority. Duplicating content creates drift and has no established upstream requirement. This is an architecture choice, not permission to move user data without migration design.

Sources:
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/AGENTS.md
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/harness/context_budget.py
- local `.agents/AGENTS.md`, `.agents/PREFERENCES.md`

## Exact append-only conflict

Local `ageroot_skills/AGENTS.md`: preserve append-only episodic and semantic JSONL. Current local memory-manager also forbids deleting/truncating/rewriting source data and makes candidate records immutable, review events append-only. Local retention archives copies.

Upstream deviations:
- auto_dream.py `_write_entries_locked`: os.ftruncate(fd, 0), then rewrite retained episodes. run_dream_cycle calls it after decay. Locking prevents concurrent loss but does not preserve append-only.
- decay.py removes qualifying >90-day, salience<2 episodes from active retained list after archival.
- archive.py:18 shutil.move(WORKSPACE.md, snapshot) after 2-day staleness.
- promote.py can remove prior candidate from old lifecycle subdirectory at line 174; review_state stores lifecycle in mutable candidate records/directories. This conflicts with existing stronger candidate immutability, though local repository-level hard rule only explicitly names episodic/semantic JSONL.
- render_lessons.py is generated projection machinery; rewriting LESSONS.md is expected and must not be confused with source JSONL mutation.

Sources:
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/auto_dream.py
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/decay.py
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/archive.py
- https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/promote.py

## Update-friendly options (design inferences)

1. Pinned vendored upstream memory closure, preserve filenames/import layout; explicit source revision+manifest, Apache license/attribution; small documented patches for configurable data paths, three categories and append-only retention. Test patch application against each upstream update. Most compatible with requested supportability while respecting current repository rules.
2. Pristine upstream operating on a disposable projection of append-only data. Avoid source mutation but requires synchronization and candidate identity/state mapping; more integration complexity than a few focused patches.
3. Exact upstream mutable memory behavior requires explicit decision to change local append-only contract. Full-runtime preference alone should not silently change that contract.

Three-directory layout also requires routing upstream working/REVIEW_QUEUE.md and candidates into approved places, plus deciding where .features.json/.index live. Removing working implies adapting context loader and stale workspace archival, or supplying a planning-with-files bridge.

## Verification / changes / limits

Only this report written. No code/data modified, no tests run (discovery scope). GitHub API rate limit reached while fetching later adapter and README/requirements files; first-pass scan results are preserved here. No authenticated credentials accessed and no domain-policy bypass attempted. Further scheduler specifics need later approved read once rate limit clears or existing local upstream checkout becomes available.
