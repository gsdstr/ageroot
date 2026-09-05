# Ageroot

Ageroot renders and updates a portable agent-infrastructure stack in a project. This context names its update safety concepts and project-memory responsibilities.

## Language

**Safety-first dry-run comparison**:
A strategy-aware pre-apply assessment that distinguishes intended generated changes from local modifications and conflicts before any update can be applied.
_Avoid_: file diff, sync check

**Hybrid baseline**:
The comparison basis that uses current, newly rendered, and prior rendered versions for renderer-owned strategies; external links have no content baseline and are validated separately.
_Avoid_: universal baseline, state-only comparison

**Proposed region merge**:
A deterministic dry-run result for a managed-regions file with intact region markers that preserves declared user regions and replaces only declared generated regions; it warns about local edits and is shown for confirmation before application.
_Avoid_: automatic overwrite, whole-file merge

**Malformed region structure**:
A managed-regions file whose declared region markers are missing, unpaired, moved, or otherwise fail structural validation. It is a blocking conflict because no safe proposed region merge can be calculated.
_Avoid_: mergeable local edit, recoverable marker drift

**Rendered baseline snapshot**:
The complete, separately stored result of an approved render for a renderer-owned file. State references the snapshot and records its SHA-256 for integrity verification.
_Avoid_: inline state content, hash-only baseline

**Unverified comparison**:
A two-way comparison between a current renderer-owned file and its new render when snapshot persistence is disabled. It cannot classify local modifications and is explicitly labelled before confirmation.
_Avoid_: safety-first classification, conflict check

**External-link validation**:
A dry-run check that an external link exists and resolves to its expected target. It reports link state only; Ageroot neither compares target content nor applies changes to it.
_Avoid_: external-link content diff, external-link update

**Snapshot persistence policy**:
An installation-wide configuration setting that enables or disables rendered baseline snapshot storage for every renderer-owned file.
_Avoid_: per-file snapshot policy, per-strategy snapshot policy

**Summary-first confirmation**:
An approval rule under which a concise dry-run summary is sufficient for confirmation, while complete diffs remain available on request.
_Avoid_: mandatory-diff confirmation, diff-free confirmation

**Tiered confirmation summary**:
A concise report that gives counts for changed and unchanged files, and path-level reasons, apply eligibility, and a full-diff access method only for conflicts and blocked files.
_Avoid_: all-path summary, content-in-summary

**Atomic apply**:
An approval outcome that applies the entire update only when every renderer-owned path is eligible. Any conflict or blocked path prevents all managed changes.
_Avoid_: partial apply, per-path confirmation

**Snapshot integrity escalation**:
A required explicit user decision when snapshot persistence is enabled but a baseline snapshot is missing or fails SHA-256 verification. No update is applied automatically.
_Avoid_: silent unverified fallback, automatic baseline replacement

**One-time unverified override**:
An explicit, single-update user approval to use an unverified comparison after snapshot integrity escalation. It does not replace or repair the stored baseline.
_Avoid_: persistent integrity bypass, baseline acceptance

**Transactional snapshot commit**:
The atomic persistence of every new rendered baseline snapshot, its SHA-256, and state only after every managed change has applied successfully.
_Avoid_: per-file snapshot commit, deferred snapshot update

**Deletion escalation**:
A required, separate explicit confirmation for a renderer-owned managed file that is absent from a new render. Its presence blocks the ordinary update flow.
_Avoid_: ordinary update deletion, implicit removal

**Locally modified deletion**:
A proposed deletion whose current file differs from its rendered baseline. It is blocked until the user manually preserves or relocates the file and repeats the dry run.
_Avoid_: confirmed destructive deletion, snapshot backup

**Snapshot store**:
The project-local `.agents/snapshots/` directory that holds rendered baseline snapshots. It is excluded from Git.
_Avoid_: tracked snapshot store, user-home snapshot store

**Unverified migration bootstrap**:
The first dry run for an existing installation with snapshot persistence enabled but no snapshot store. It requires explicit confirmation and creates baseline snapshots only after a successful apply.
_Avoid_: implicit baseline adoption, mandatory manual migration

**Deterministic content normalization**:
Comparison preprocessing that removes line-ending, final-newline, trailing-whitespace, and formatter-only Markdown/YAML noise without changing YAML data, key order, Markdown structure, or text.
_Avoid_: semantic normalization, lossy formatting

**Comparison result class**:
The fixed outcome vocabulary for one managed path: `unchanged`, `changed`, `unverified`, `region-merge`, `conflict`, `blocked`, `invalid-link`, or `deletion-pending`.
_Avoid_: ad-hoc status, ambiguous warning

**Memory workflow**:
Use of project memory while carrying out a task, including retrieval, recording experiences, and explicit review of proposed knowledge. It adds to experience and knowledge histories without replacing existing entries.
_Avoid_: memory maintenance, task planning

**Memory maintenance**:
Work on accumulated project memory outside the active task, including synthesis, archival, cleanup, and search-index upkeep. It may reorganize stored memory but does not automatically accept proposed knowledge.
_Avoid_: memory workflow, automatic knowledge acceptance

**Project preferences**:
User-authored conventions for a specific project, distinct from experiences and knowledge accumulated by agents. They have one authoritative record and are referenced by the agent instructions.
_Avoid_: personal memory, learned preferences
