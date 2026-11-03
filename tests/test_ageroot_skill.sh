#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RUNNER="$REPO_ROOT/skills/ageroot/scripts/ageroot.py"

echo "=== Testing ageroot skill CLI help output ==="
python3 "$RUNNER" --help > /dev/null
python3 "$RUNNER" check --help > /dev/null
python3 "$RUNNER" plan --help > /dev/null
python3 "$RUNNER" apply --help > /dev/null

echo "=== Testing ageroot skill check, plan, and apply in isolated directory ==="
TEMP_DIR="$(mktemp -d /tmp/ageroot_skill_test_XXXXXX)"
trap 'rm -rf "$TEMP_DIR"' EXIT

# Export canonical distribution payload into temp target
PYTHONPATH=packages python3 -m ageroot_core.distribution --export "$TEMP_DIR"

# Run check on freshly exported target
python3 "$RUNNER" check --repo-root "$REPO_ROOT" --target "$TEMP_DIR"

# Run plan (dry run) on target
python3 "$RUNNER" plan --repo-root "$REPO_ROOT" --target "$TEMP_DIR"

# Run apply on target
python3 "$RUNNER" apply --repo-root "$REPO_ROOT" --target "$TEMP_DIR"

echo "Ageroot skill CLI tests passed successfully!"
