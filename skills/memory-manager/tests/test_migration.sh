#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SCRIPT="$ROOT/scripts/memory_manager.py"
FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/memory-migration.XXXXXX")
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

MEMORY="$FIXTURE/memory"
mkdir -p "$MEMORY"

# Legacy DECISIONS.md at root
printf '%s\n' '# Legacy Architecture Decisions' '## Decision 1' > "$MEMORY/DECISIONS.md"
# Legacy AGENT_LEARNINGS.jsonl at root
printf '%s\n' '{"timestamp":"2026-09-01T00:00:00Z","action":"legacy action","result":"success"}' > "$MEMORY/AGENT_LEARNINGS.jsonl"

# Preview
preview_out=$(python3 "$SCRIPT" --memory-root "$MEMORY" migrate-preview)
echo "$preview_out" | grep -F '"status": "ready"' >/dev/null

# Apply
apply_out=$(python3 "$SCRIPT" --memory-root "$MEMORY" migrate-apply)
echo "$apply_out" | grep -F '"status": "applied"' >/dev/null

[ -f "$MEMORY/semantic/DECISIONS.md" ]
grep -F '# Legacy Architecture Decisions' "$MEMORY/semantic/DECISIONS.md" >/dev/null
[ -f "$MEMORY/episodic/AGENT_LEARNINGS.jsonl" ]
grep -F 'legacy action' "$MEMORY/episodic/AGENT_LEARNINGS.jsonl" >/dev/null

# Idempotency check: repeat apply should succeed without duplication
python3 "$SCRIPT" --memory-root "$MEMORY" migrate-apply >/dev/null
[ "$(wc -l < "$MEMORY/episodic/AGENT_LEARNINGS.jsonl" | tr -d ' ')" = "1" ]

# Conflict check: modify target DECISIONS.md with differing content
printf '%s\n' '# Conflicting Content' > "$MEMORY/semantic/DECISIONS.md"
preview_conflict=$(python3 "$SCRIPT" --memory-root "$MEMORY" migrate-preview)
echo "$preview_conflict" | grep -F '"status": "conflict"' >/dev/null

if python3 "$SCRIPT" --memory-root "$MEMORY" migrate-apply 2>/dev/null; then
  echo "Expected migration apply to fail on conflict"
  exit 1
fi

echo 'memory-migration: PASS'
