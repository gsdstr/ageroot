#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MAINTENANCE="$ROOT/scripts/memory_maintenance.py"
MANAGER="$ROOT/../memory-manager/scripts/memory_manager.py"
REFLECT="$ROOT/../memory-manager/scripts/memory_reflect.py"

FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/memory-maintenance.XXXXXX")
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

MEMORY="$FIXTURE/memory"
mkdir -p "$MEMORY/episodic"

# Seed episodes with high pain/importance and sufficient reflection length so heuristic prefilter passes
python3 "$REFLECT" --memory-root "$MEMORY" sample 'serialize UTC timestamps across boundaries' 'completed without errors' --note 'Serialize timestamps in UTC across distributed service boundaries to ensure consistent ordering' --pain 8 --importance 8 >/dev/null
python3 "$REFLECT" --memory-root "$MEMORY" sample 'serialize UTC timestamps across boundaries' 'completed without errors' --note 'Serialize timestamps in UTC across distributed service boundaries to ensure consistent ordering' --pain 8 --importance 8 >/dev/null

# Dry run
dry_out=$(python3 "$MAINTENANCE" --memory-root "$MEMORY" --dry-run)
echo "$dry_out" | grep -F 'patterns=' >/dev/null

# Apply maintenance
apply_out=$(python3 "$MAINTENANCE" --memory-root "$MEMORY")
echo "$apply_out" | grep -F 'staged=1' >/dev/null

[ -f "$MEMORY/REVIEW_QUEUE.md" ]
grep -F 'Review Queue' "$MEMORY/REVIEW_QUEUE.md" >/dev/null
[ -f "$MEMORY/.index/memory.db" ]

# Verify candidate staged by maintenance
candidates=$(python3 "$MANAGER" --memory-root "$MEMORY" list)
echo "$candidates" | grep -F 'staged' >/dev/null

# Missing runtime error check
if python3 "$MAINTENANCE" --memory-root "$MEMORY" --manager-runtime "$FIXTURE/nonexistent" 2>/dev/null; then
  echo "Expected failure with missing runtime"
  exit 1
fi

echo 'memory-maintenance: PASS'
