# Ageroot Template as a Drop-in

**Status:** proposed — this document defines the target boundary only; it does
not change the template repository layout.

## Goal

Make `ageroot_template/` a copyable Ageroot payload. Its tracked product surface
contains exactly the root `AGENTS.md` adapter and the `.agents/` infrastructure
tree.

## Package boundary

Included:

- `AGENTS.md` — adapter entry point for supported agent harnesses.
- `.agents/` — generated instructions, configuration/state examples, protocols,
  rules, skills links, and `.agents/ageroot_core/` comparison runtime with tests.

Excluded:

- Build/package metadata, release scripts, README, plugin manifests, and other
  repository-development tooling.
- `.planning/` — owned by planning-with-files and never an Ageroot-managed path.
- `.scratch/` — local design/issue material and never part of the drop-in.

## Installation contract

1. Copy `AGENTS.md` and `.agents/` into a consuming repository.
2. Fill installation-specific values in `.agents/ageroot.config.yaml`.
3. Render managed files and run safety-first comparison before any update.
4. Exclude `.planning/` from discovery, rendering, comparison, and reports.
5. Treat a diff limited to `generated-by` provenance fields as metadata-only:
   classify it `unchanged` and omit it from the diff.

## Acceptance criteria

- `git ls-files` in `ageroot_template/` lists only `AGENTS.md` or paths beneath
  `.agents/`.
- `PYTHONPATH=.agents python3 -m unittest discover -s .agents/ageroot_core/tests`
  passes.
- The drop-in contains no package-management or release-tool dependency.
