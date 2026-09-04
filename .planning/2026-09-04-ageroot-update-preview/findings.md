# Findings & Decisions

## Requirements

- Preview updated `./ageroot_template` in the current worktree only.
- Render every managed template; run the safety-first comparison; show complete diff.
- Do not apply, change Ageroot state, or commit before explicit confirmation.

## Research Findings

- Current state lists six generated paths/groups and one `external-link` skill directory.
- Snapshot policy is enabled, but state is legacy: it has neither snapshot references nor hashes. Comparisons must be labeled `unverified`.
- Root `AGENTS.md` is not state-managed and remains user-owned.
- Five generated files have proposed changes: metadata markers in four files and a substantive rewrite of `.agents/rules/rtk-rules.md`.
- All three concrete protocol files are byte-identical to the render. The skills directory exists and has valid child symlinks.
- The comparison runtime raises `IsADirectoryError` for the managed directory entry `.agents/protocols/`; it cannot safely render/compare/snapshot that path. It also is absent from the managed-path list, so the template's new `.agents/ageroot_core/` runtime would not be installed.
- Per additional user requirements, `.planning/` is excluded from Ageroot discovery/render/comparison/reporting, and marker-only generated-by metadata differences classify as unchanged. Under this rule, four generated Markdown files are unchanged; only the RTK rules file has a substantive proposed difference.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Render to temporary directory | Ensures dry-run cannot modify installed outputs. |
| Do not offer ordinary apply confirmation | Atomic apply is blocked until the state model is migrated from directory to individual protocol entries (and, if desired, includes the comparison runtime). |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| None | N/A |
