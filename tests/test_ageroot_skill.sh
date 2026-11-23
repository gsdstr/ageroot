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

echo "=== Testing auto-resolution of repo root without --repo-root argument ==="
python3 "$RUNNER" plan --target "$TEMP_DIR"

echo "=== Testing auto-resolution via flat template_repo_root in global config ==="
MOCK_HOME="$(mktemp -d /tmp/ageroot_mock_home_XXXXXX)"
ISOLATED_RUNNER_DIR="$(mktemp -d /tmp/ageroot_isolated_runner_XXXXXX)"
cp "$RUNNER" "$ISOLATED_RUNNER_DIR/ageroot.py"
mkdir -p "$MOCK_HOME/.config/ageroot"
echo "template_repo_root: $REPO_ROOT" > "$MOCK_HOME/.config/ageroot/config.yaml"
PYTHONPATH="$REPO_ROOT/packages" HOME="$MOCK_HOME" XDG_CONFIG_HOME="$MOCK_HOME/.config" python3 "$ISOLATED_RUNNER_DIR/ageroot.py" plan --target "$TEMP_DIR"
rm -rf "$MOCK_HOME" "$ISOLATED_RUNNER_DIR"

echo "=== Testing snapshot-sync after wiping snapshots ==="
rm -rf "$TEMP_DIR/.agents/snapshots"
python3 "$RUNNER" snapshot-sync --target "$TEMP_DIR"
test -d "$TEMP_DIR/.agents/snapshots"

echo "=== Testing self-healing plan when snapshots are missing ==="
rm -rf "$TEMP_DIR/.agents/snapshots"
python3 "$RUNNER" plan --target "$TEMP_DIR"
test -d "$TEMP_DIR/.agents/snapshots"

echo "Ageroot skill CLI tests passed successfully!"
