#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== 1. Ageroot Core & Distribution Tests ==="
PYTHONPATH=packages python3 -m unittest discover -s packages/ageroot_core/tests -v

echo ""
echo "=== 2. Orchestration Package Sync Check ==="
python3 scripts/sync-orchestration-package.py --check

echo ""
echo "=== 3. Memory Skills Lifecycle & Concurrency Tests ==="
sh skills/tests/run_all.sh

echo ""
echo "=== 4. Distribution Whole-Payload Export & Drift Check ==="
TEMP_EXPORT="$(mktemp -d /tmp/ageroot_test_export_XXXXXX)"
trap 'rm -rf "$TEMP_EXPORT"' EXIT

PYTHONPATH=packages python3 -m ageroot_core.distribution --export "$TEMP_EXPORT"
PYTHONPATH=packages python3 -m ageroot_core.distribution --check --target "$TEMP_EXPORT"

echo ""
echo "========================================="
echo "ALL TEST SUITES PASSED (Core, Dist, Memory, Orchestration)"
echo "========================================="
