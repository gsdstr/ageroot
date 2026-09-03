# Architecture Decisions

## Stack update model

**Status:** accepted

The stack is a renderer, not a file synchronizer. Installation and updates render
template sources using installation-specific configuration.

- The stack name is `Ageroot`.
- Store stack state and configuration under `.agents/`, not a top-level
  `.agentic-stack/` directory.
- Use `.agents/ageroot.state.yaml` and `.agents/ageroot.config.yaml` to avoid
  collisions with other `.agents/` conventions.
- Rendered Markdown files include a generated-file comment with stack name,
  template version, and render timestamp.
- The state file is the authority for managed paths and each path's render
  strategy; generated-file comments are informative only.
- Users may modify every deployed file. The update policy is explicit per file:
  `generated`, `managed-regions`, `seed-once`, or `external-link`.
- Every update starts with a dry run. It evaluates each managed file, produces a
  diff and concise summary, and waits for explicit user confirmation before
  applying any change.
- `SETUP.md` is a clean generated instruction file and follows the dry-run
  confirmation protocol.
- `PREFERENCES.md` is generated from its template and remains user-editable. Its
  changes are included in the normal dry-run diff and require confirmation before
  an update applies.
- Skills remain `external-link`: `skills-manager` manages symlinks to the shared
  `~/.skills-manager` store; stack updates do not copy or render skill contents.

## Open questions

- Improve the file-comparison protocol in a later iteration.
- Define the user-override contract for files using `managed-regions`.
