#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MANAGER="$ROOT/../memory-manager/scripts/memory_manager.py"
REFLECT="$ROOT/../memory-manager/scripts/memory_reflect.py"
MAINTENANCE="$ROOT/scripts/memory_maintenance.py"

FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/memory-concurrency.XXXXXX")
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

MEMORY="$FIXTURE/memory"
mkdir -p "$MEMORY/episodic"

# Concurrent appends while maintenance runs
for i in $(seq 1 10); do
  python3 "$REFLECT" --memory-root "$MEMORY" test "action $i" "outcome $i" --importance 5 >/dev/null &
done

python3 "$MAINTENANCE" --memory-root "$MEMORY" >/dev/null

wait

count=$(wc -l < "$MEMORY/episodic/AGENT_LEARNINGS.jsonl" | tr -d ' ')
[ "$count" -eq 10 ]

echo 'memory-concurrency: PASS'
