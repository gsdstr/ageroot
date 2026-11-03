---
name: memory-maintenance
description: Perform offline memory clustering, candidate staging, decay/archival, review queue updates, and FTS rebuilds. Depends on memory-manager.
---

# Memory maintenance

Use this skill for explicit maintenance of project memory. It depends on the
shared runtime provided by `memory-manager`.

## Operating rules

- Run explicitly outside active task work. It is never invoked automatically on
  session end or task completion.
- Clusters recurring episodic experiences and stages candidate patterns for review.
- Never automatically accepts proposed knowledge; acceptance remains an explicit
  review action in `memory-manager`.
- Applies decay and archival to stale low-salience episodes. Maintenance may
  rewrite retained episodic journals using crash-safe atomic replace under a bounded root lock.
- Updates `REVIEW_QUEUE.md` and rebuilds the `.index/memory.db` FTS5 index.

## Dependency

`memory-maintenance` requires the `memory-manager` runtime. If `memory-manager` is
missing or incompatible, the command exits with a clear error. Override the
runtime directory using `--manager-runtime <path>` or `MEMORY_MANAGER_RUNTIME` if
needed.

## Invocation

```sh
MAINTENANCE=.agents/skills/memory-maintenance/scripts/memory_maintenance.py

# Run explicit maintenance cycle
python3 "$MAINTENANCE" --memory-root .agents/memory

# Dry-run preview without mutations
python3 "$MAINTENANCE" --memory-root .agents/memory --dry-run
```
