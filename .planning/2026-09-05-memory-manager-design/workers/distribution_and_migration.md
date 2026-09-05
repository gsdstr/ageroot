# Distribution and migration facts — third round

Bounded local read-only inspection. User decisions supplied by coordinator: external .agents/PREFERENCES.md; episodic and semantic categories; memory-manager working workflow append-only; memory-maintenance permitted upstream housekeeping rewrites; review in manager; FTS5 first. This report records facts and inferences, not implementation instructions.

## Repository and installed topology

- `ageroot_skills/.git` is a real directory: nested independent Git repository. Root `.gitmodules` absent; no Git submodule contract established by these paths.
- `.agents/SKILLS.md` mandates skills-manager installation/update/removal; consumers symlink into `~/.skills-manager`; do not copy skills into consumer or edit linked installed contents. Global required skills allowed without local link.
- Current project `.agents/skills/memory-manager` and `memory-auto-dream` paths absent.
- Shared store has real directories for memory-manager, memory-auto-dream, memory-clustering, memory-retention, memory-runtime-cleanup. Their SKILL.md bytes equal development repo copies. This check does not prove all runtime bytes or versions equal.
- No package manifest/dependency lock surfaced in bounded rg file inventory of ageroot_skills; current contract is skill docs plus scripts/tests.
- `ageroot_skills/AGENTS.md` currently says each skill self-contained. Existing auto-dream is already operationally dependent on sibling clustering/manager, so contract and implementation have tension.

## How sibling resolution works now

`ageroot_skills/skills/memory-auto-dream/scripts/run_dream.py` resolves `Path(__file__).resolve().parents[2]`, then sibling memory-clustering/scripts/cluster_patterns.py and memory-manager/scripts/memory_manager.py. Explicit `--cluster-script` and `--manager-script` override.

For a normal consumer symlink, resolve follows to installed store path, so sibling lookup uses shared store, not consumer .agents/skills. Works if both skills installed as siblings in same store; fails if only maintenance is installed or manager is located elsewhere, unless explicit path override supplied. Current command calls python3 subprocess, with no version/compatibility handshake visible.

## Runtime ownership options — inference

One runtime copy under memory-manager, memory-maintenance entry point depends on that runtime:
- Smallest upstream update surface; no duplicated modules and no competing writer implementations.
- Document manager as required dependency; explicit resolver override and clear missing/incompatible-runtime error.
- Version both skill entry points together or verify compatible runtime version.
- Clarify self-contained rule to allow explicit intra-repository dependency, matching existing auto-dream practice.

Duplicated self-contained runtime per skill:
- Independent installation works without sibling resolution.
- Copies drift under independent skills-manager updates; both write same data schema, so version compatibility remains necessary.
- Shared source generation/checksum checks could prevent drift in repository but cannot guarantee consumers update both together.

Given supportability objective and two deliberately related skills, one runtime with explicit dependency appears smaller maintenance burden. This is a recommendation requiring design decision, not an assertion that installer automatically handles dependencies.

## Existing working commands and append-only boundary

`memory-manager/scripts/memory_manager.py`:
- `json_line` opens source JSONL in append mode (lines 21-24).
- `stage` creates immutable candidate JSON and appends staged event (109-126).
- `accept` appends semantic lesson then accepted event (158-178); it does not call render automatically.
- reject/reopen append candidate events, preserving candidate JSON (181-194).
- retract appends another semantic record with same lesson id plus retracted status (197-208).
- `render` rewrites LESSONS.md managed projection, preserving pre-sentinel preamble (211-232); existing file without sentinel requires --adopt-existing.
- No equivalent fcntl lock in this CLI; reflection CLI has optional fcntl. Existing tests do not establish concurrent maintenance/manager safety.

Important design detail: working skill can preserve append-only authoritative records while refreshing generated projections. Strictly banning all rewrites would exclude current render behavior, and FTS query may rebuild derived cache upstream. Define append-only for authoritative episodic/semantic records, with documented generated-file exceptions.

Review placement needs consistency: upstream candidate review mutates candidate lifecycle files, while existing local manager uses immutable candidate + event journal. Allowing maintenance rewrites alone does not resolve whether working review keeps current event model or adopts upstream candidate mutations. Parent should distinguish authoritative episode/lesson append-only from every file immutable.

## Actual local legacy memory — paths/counts only

- `.agents/memory/` exists, contains only `DECISIONS.md` (1650 bytes).
- No child episodic/, semantic/, personal/, working/, candidates/ in that root.
- `.agent/memory/` absent.
- `ageroot_template/.agents/memory` and `.agent/memory` absent; bounded recursive inventory found no directory named memory anywhere in ageroot_template or ageroot_skills outside .git.
- Thus no detected populated JSONL lifecycle migration in current consumer. Existing root DECISIONS.md is a migration/source-of-truth placement question, not permission to discard it. Its content was not read for this task.
- External .agents/PREFERENCES.md already exists as startup authority from earlier inspection; no personal memory copy detected.

## Tests and verification contract

`ageroot_skills/tests/run_all.sh` runs lifecycle, reflection, clustering, dream, retention, cleanup shell suites. All current skill tests designed for temporary memory roots.

Read lifecycle test asserts candidate checksum unchanged across acceptance/retraction, review event count, appended semantic retraction, preserved LESSONS.md preamble and exclusion of retracted claim. Dream test asserts dry-run no candidates then --apply stages one through sibling paths.

Missing coverage for new design: installed symlink topology, missing/incompatible manager dependency, root relocation, two-skill installation, concurrent writer/maintenance lock behavior, FTS cache lifecycle. These are bounded future verification targets, not tests added now.

## Changes and limits

Only this report written. No installed skill updates, repository source edits, memory reads beyond paths/size inventory, network requests, test execution or agent session access. No upstream checkout cache created in earlier worker calls (HTTP content existed only in process output); not searched in session records.
