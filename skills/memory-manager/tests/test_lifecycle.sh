#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SCRIPT="$ROOT/scripts/memory_manager.py"
FIXTURE=$(mktemp -d "${TMPDIR:-/tmp}/memory-manager.XXXXXX")
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

python3 "$SCRIPT" --help >/dev/null

MEMORY="$FIXTURE/memory"
mkdir -p "$MEMORY/semantic"
printf '%s\n' '# Curated preamble' > "$MEMORY/semantic/LESSONS.md"

# 1. Stage candidate
python3 "$SCRIPT" --memory-root "$MEMORY" stage --id alpha --claim 'Serialize timestamps in UTC across service boundaries' --evidence run-1 --reviewer test >/dev/null

# 2. Accept candidate
candidate_before=$(cksum "$MEMORY/candidates/alpha.json")
python3 "$SCRIPT" --memory-root "$MEMORY" accept alpha --reviewer test --rationale 'Repeated evidence' >/dev/null

# 3. Search via FTS / keyword
python3 "$SCRIPT" --memory-root "$MEMORY" search 'timestamps UTC' | grep -F 'semantic/lessons.jsonl' >/dev/null

# 4. Intent-based recall
python3 "$SCRIPT" --memory-root "$MEMORY" recall 'handle timestamps in UTC' | grep -F 'Serialize timestamps in UTC' >/dev/null

# 5. Review workflows: reject and reopen
python3 "$SCRIPT" --memory-root "$MEMORY" stage --id beta --claim 'Validate memory lifecycle transitions in a temporary fixture' --reviewer test >/dev/null
python3 "$SCRIPT" --memory-root "$MEMORY" reject beta --reviewer test --reason 'Need more evidence'
[ -f "$MEMORY/candidates/rejected/beta.json" ]
python3 "$SCRIPT" --memory-root "$MEMORY" reopen beta --reviewer test
[ -f "$MEMORY/candidates/beta.json" ]
python3 "$SCRIPT" --memory-root "$MEMORY" reject beta --reviewer test --reason 'Still insufficient evidence'

# 6. Retraction is append-only
before=$(wc -l < "$MEMORY/semantic/lessons.jsonl")
python3 "$SCRIPT" --memory-root "$MEMORY" retract lesson_alpha --reviewer test --rationale 'Fixture retraction' >/dev/null
after=$(wc -l < "$MEMORY/semantic/lessons.jsonl")
[ "$after" -gt "$before" ]

# 7. Render LESSONS.md
python3 "$SCRIPT" --memory-root "$MEMORY" render --adopt-existing >/dev/null
grep -F '# Curated preamble' "$MEMORY/semantic/LESSONS.md" >/dev/null
grep -F 'memory-manager:generated' "$MEMORY/semantic/LESSONS.md" >/dev/null
! grep -F 'Serialize timestamps in UTC across service boundaries  <!-- status=accepted' "$MEMORY/semantic/LESSONS.md" >/dev/null

# 8. Event log check
[ "$(wc -l < "$MEMORY/candidates/events.jsonl")" -eq 6 ]
grep -F '"action": "rejected"' "$MEMORY/candidates/events.jsonl" >/dev/null
grep -F '"status": "retracted"' "$MEMORY/semantic/lessons.jsonl" >/dev/null

# 9. Config JSON resolver
printf '{"memory_root":"%s"}\n' "$MEMORY" > "$FIXTURE/config.json"
python3 "$SCRIPT" --config "$FIXTURE/config.json" list | grep -F 'beta' >/dev/null

# 10. Rebuild index
python3 "$SCRIPT" --memory-root "$MEMORY" rebuild-index | grep -F 'Index rebuilt' >/dev/null

echo 'memory-manager lifecycle: PASS'
