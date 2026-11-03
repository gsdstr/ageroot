# Memory lifecycle extraction audit

Audited upstream source: `https://github.com/codejunkie99/agentic-stack` at commit `9424c58e1cfc17a709d1adfa13678e876edfe409`.

| Upstream module / tool | Skill owner | Functionality & Adaptation |
|---|---|---|
| `.agent/memory/render_lessons.py` | `memory-manager` | Derives `semantic/LESSONS.md` from `semantic/lessons.jsonl` with managed sentinel. |
| `.agent/memory/validate.py` | `memory-manager` / `memory-maintenance` | Deterministic length and exact duplicate prefiltering; explicit reviewer gate for acceptance. |
| `.agent/memory/review_state.py`, `promote.py` | `memory-manager` / `memory-maintenance` | Candidate lifecycle (staged / graduated / rejected) and `REVIEW_QUEUE.md` upkeep. |
| `.agent/memory/memory_search.py` | `memory-manager` / `memory-maintenance` | SQLite FTS5 search (enabled by default) with automatic query-time rebuild and rg/grep fallback. |
| `.agent/memory/cluster.py`, `auto_dream.py` | `memory-maintenance` | Offline clustering and candidate staging; never auto-accepts knowledge. |
| `.agent/memory/decay.py`, `archive.py` | `memory-maintenance` | Low-salience decay and episodic snapshot archiving; crash-safe atomic replace under bounded lock. |
| `.agent/tools/memory_reflect.py`, `post_execution.py`, `on_failure.py` | `memory-manager` | Append-only episodic success/failure records with consumer repo commit SHA provenance and failure threshold tracking. |
| `.agent/tools/learn.py`, `graduate.py`, `reject.py`, `reopen.py`, `retract_lesson.py`, `list_candidates.py`, `recall.py` | `memory-manager` | Portable lifecycle CLI subcommands (`stage`, `accept`, `reject`, `reopen`, `retract`, `list`, `recall`). |

All project memory and auxiliary state (`episodic/`, `semantic/`, `candidates/`, `.index/`, `.features.json`, `REVIEW_QUEUE.md`) remain project-owned and Git-trackable.
