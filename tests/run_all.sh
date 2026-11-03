#!/bin/sh
set -eu

for test in \
  skills/memory-manager/tests/test_lifecycle.sh \
  skills/memory-manager/tests/test_reflect.sh \
  skills/memory-manager/tests/test_migration.sh \
  skills/memory-maintenance/tests/test_maintenance.sh \
  skills/memory-maintenance/tests/test_concurrency.sh \
  tests/test_ageroot_skill.sh
do
  sh "$test"
done
