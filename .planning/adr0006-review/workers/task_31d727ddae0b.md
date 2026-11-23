# ADR-0006 implementation worker

Read ADR and repository contracts. Existing uncommitted GLOSSARY/ADR belong to coordinator.

Phases: implement standalone roles; relocate orchestration; integrate distribution; verify acceptance.

Roles, skills, adapter, and distribution integrated. Initial tests exposed macOS /var symlink expectations; normalized fixture paths. Template .gitignore did not exist; created it. A stray shell placeholder failed after writing SKILL.md; no content impact.

Standard local dry-run found six pre-existing corrupt snapshots, blocking apply. Coordinator explicitly instructed: finish source/tests; leave local state migration documented, no force apply. Added baseline-backed regression tests for standard migration, deletion confirmation, and modified legacy safety.

## Final implementation

- Added standalone `skills/ageroot-roles/scripts/roles.py`, SKILL instructions, and 25 unittest methods (including invalid-parser subcases for malformed shapes, duplicate keys, numeric/boolean scalars, and unsupported YAML). Strict block-YAML validation reports source/line, rejects duplicate keys/invalid shapes, supports explicit disablement, and has no non-stdlib imports or ageroot_core dependency.
- Implemented per-role four-layer hierarchy, whole-list replacement, strict exhaustion, ordered PATH readiness, exclusion traces, workspace/root flags before/after commands, upward discovery, text/JSON show, and atomic scoped setup.
- Relocated complete orchestration package and Orca adapter into `skills/ageroot-orchestrate/`; added lifecycle instructions and 5 adapter tests alongside 9 relocated validation tests. Adapter dynamically invokes sibling roles.py, records selected harness/model and evidence, excludes Builder model/family for Reviewer, and blocks unresolved or unknown-family routing before apply/execute.
- Registered both skills as default first-party distribution components, removed former components, updated drift prefixes (retired prefix retained solely to detect stale files), APM manifests, ignore files, protocols, generated instruction pointers, README, sync tool, and consolidated tests. Removed both old orchestration source/install trees and obsolete protocols.
- Fixed existing ageroot CLI package search precedence: canonical packages now win over stale installed core, which previously broke tests after relocation.
- Added 3 distribution migration regressions: standard engine updates state and snapshots while retiring old paths; deletion still needs explicit confirmation; modified legacy files block atomic migration. Local role preferences remain unmanaged/preserved.

## Acceptance evidence

- `bash scripts/test.sh`: PASS, including 43 core/distribution tests, 14 orchestration/adapter tests, 25 roles tests, memory lifecycle/concurrency suites, isolated ageroot check/plan/apply/snapshot-sync, and whole-payload export/drift validation.
- `PYTHONPATH=packages python3 -m unittest discover -s packages/ageroot_core/tests`: PASS (43 tests). Bare command was also attempted; repository's source layout requires its established PYTHONPATH=packages setting.
- `python3 -m unittest discover -s skills/ageroot-roles/tests`: PASS (25 tests).
- `python3 skills/ageroot-orchestrate/scripts/validate.py --package`: PASS.
- `git diff --check`: PASS.
- Full consolidated test output: `/tmp/ageroot-adr0006-test.log`.

## Deferred local state migration (Coordinator instruction)

Local `.agents/ageroot.state.yaml` remains unchanged. Standard local `ageroot.py plan` detected six existing corrupt baseline snapshots: AGENTS.md, .agents/PREFERENCES.md, .agents/protocols/delegation.md, .agents/ageroot_core/__init__.py, comparison.py, and tests/test_comparison.py. No force apply, unverified override, or snapshot replacement was performed. Coordinator explicitly instructed completion of source work and tests, with local migration left as a follow-up.

Owner/Coordinator must reconcile snapshot integrity first, then rerun `python3 skills/ageroot/scripts/ageroot.py plan` and perform approved standard apply with deletion confirmation as appropriate. Migration correctness is covered in isolated regression tests. Existing GLOSSARY/ADR and coordinator scratch changes were preserved; older Portable orchestration package glossary prose still references the retired layout and may need a separate documentation refresh.
