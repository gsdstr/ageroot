---
name: memory-manager
description: Manage project-owned episodic and semantic memory safely. Use when recording reflections, staging or reviewing lesson candidates, rendering LESSONS.md, retracting a lesson, or searching memory.
---

# Memory manager

Use this skill for core memory lifecycle operations. Runtime code is owned by
this skill; memory data is project-owned and stored under the configured data root.

## Trigger

Use for: episodic success/failure reflection; candidate inspection, staging, or review;
accepting, rejecting, reopening, or retracting a lesson; rendering `LESSONS.md`;
and querying memory via SQLite FTS5 with fallback.

## Safety and mutation boundary

- Source episodic and semantic journals (`episodic/AGENT_LEARNINGS.jsonl` and
  `semantic/lessons.jsonl`) are append-only during normal task workflow.
- Knowledge acceptance is strictly an explicit human/agent review action with a
  mandatory reviewer and rationale. Automatic acceptance is never performed.
- Candidate files and derived projections (`semantic/LESSONS.md`, `.index/memory.db`,
  `REVIEW_QUEUE.md`) update during workflow operations.
- All operations synchronize using a bounded root lock (`.lock`).

## Data-path configuration

Resolution order:
1. `--memory-root`
2. `MEMORY_MANAGER_DATA_ROOT`
3. `--config` (JSON file containing `{"memory_root": "..."}`)
4. `<project-root>/.agents/memory`

Project preferences resolve independently to `<project-root>/.agents/PREFERENCES.md`.

## Workflow commands

```sh
SCRIPT=.agents/skills/memory-manager/scripts/memory_manager.py
REFLECT=.agents/skills/memory-manager/scripts/memory_reflect.py

# Record an episodic success or failure event
python3 "$REFLECT" --memory-root .agents/memory memory-manager \
  "render lesson projection" "rendered successfully" --importance 5 --evidence run-1

# Search memory with FTS5 (or fallback)
python3 "$SCRIPT" --memory-root .agents/memory search "UTC timestamps"

# Recall active lessons relevant to an intent
python3 "$SCRIPT" --memory-root .agents/memory recall "handle timestamps across services"

# Stage a candidate
python3 "$SCRIPT" --memory-root .agents/memory stage \
  --claim "Serialize timestamps in UTC for cross-region comparisons" \
  --evidence run-1 --reviewer test

# Candidate review
python3 "$SCRIPT" --memory-root .agents/memory list
python3 "$SCRIPT" --memory-root .agents/memory accept <candidate-id> \
  --reviewer lead --rationale "Confirmed across multiple incidents"
python3 "$SCRIPT" --memory-root .agents/memory reject <candidate-id> \
  --reviewer lead --reason "Too specific to legacy service"
python3 "$SCRIPT" --memory-root .agents/memory reopen <candidate-id> --reviewer lead

# Retract an accepted lesson
python3 "$SCRIPT" --memory-root .agents/memory retract lesson_<candidate-id> \
  --reviewer lead --rationale "Superseded by ISO-8601 UTC standard"

# Rebuild search index
python3 "$SCRIPT" --memory-root .agents/memory rebuild-index

# Preview and apply legacy migration
python3 "$SCRIPT" --memory-root .agents/memory migrate-preview
python3 "$SCRIPT" --memory-root .agents/memory migrate-apply
```
