# Independent ADR-0006 implementation review

Verdict: **CHANGES REQUESTED**.

## Finding

**P2 — Consumer installation never installs the local-role ignore rule.**
`templates/core/.gitignore:2` introduces `.agents/roles.local.yaml`, but
`packages/ageroot_core/distribution/manifest.py:35-74` enumerates core mappings
without mapping that template or otherwise installing the rule. Consequently,
the standard export/update path installs `ageroot-roles` but does not ensure
its default `setup --local` output is ignored. A consumer can accidentally
commit machine-specific preferences, contrary to ADR-0006's workspace-local
configuration contract. Root repository's ignore rule protects this repository
only. Reproduction with `collect_payload(Path.cwd())` yields no `.gitignore`
key; a temporary `DistributionService.export_payload(...)` has no `.gitignore`
yet `check_drift(...)` returns `(True, [])`. Integrate the rule using a safe
consumer update strategy preserving existing ignore entries, and test both
new installation and existing consumer ignore files.

## F1–F8 verification

- F1: PASS. Independent per-role winning layers; complete list replacement;
  exhausted explicit lists do not cross layers; empty lists disable; every
  existing layer validated; duplicate keys and invalid shapes have source/line
  diagnostics.
- F2: PASS. Static resolution uses local PATH checks only, performs no execution,
  writes, provider calls, or network probes. Known present harnesses report
  supported; other present harnesses unverified; absent binaries missing.
  Model entitlement remains explicitly unverified.
- F3: PASS. Repeatable model/family exclusion flags exist. Adapter passes Builder
  model/family when resolving Reviewer and blocks unknown Builder family.
  Isolated Reviewer worker context remains orchestration policy; adapter is a
  planner and does not dispatch workers.
- F4: PASS. Adapter and runbook no longer contain concrete model tables. Adapter
  invokes the sibling roles script dynamically; source and installed layouts
  preserve that sibling relationship.
- F5: PARTIAL. New skills are default components; old components/source paths
  removed; stale installed paths remain detectable as drift. Baseline-backed
  migration, deletion approval, and modified legacy safety tests pass. Consumer
  ignore-rule delivery is missing as described above. Local repository state
  migration remains explicitly deferred by coordinator instruction due to
  pre-existing corrupt snapshots; implementation report documents this.
- F6: PASS. Role router uses standard library only, with no ageroot_core import
  or PYTHONPATH requirement. Its subprocess tests use isolated Python `-I`.
- F7: PASS. Both root and template APM manifests declare both new skills.
- F8: PASS. Workspace/root aliases before and after subcommands, upward
  discovery, versioned JSON stdout, and stderr configuration diagnostics pass.

## Execution evidence

- `bash scripts/test.sh`: PASS, exit 0. Includes 43 core/distribution tests,
  14 orchestration/adapter tests, 25 role tests, memory lifecycle/concurrency,
  isolated CLI migration checks, whole-payload export and drift validation.
- `python3 skills/ageroot-roles/tests/test_roles.py`: PASS, 25 tests, exit 0.
- `git diff --check`: PASS.
- Git status before and after tests matches; no implementation files changed
  during review. Only this worker report was written.

No subagents, helper workers, live Orca state mutations, source edits, or
local state migration performed. Fix ignore-rule delivery and add consumer
coverage before acceptance.
