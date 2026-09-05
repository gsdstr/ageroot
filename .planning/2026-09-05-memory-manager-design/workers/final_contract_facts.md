# Final contract facts

Bounded read-only round. No new network. Upstream facts below come from full source already retrieved in earlier worker calls at revision `9424c58e1cfc17a709d1adfa13678e876edfe409`, not agent session records. Current accepted spec read from `.scratch/memory-skills/spec.md`.

## FTS behavior verified from source

Source: https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/memory_search.py

- Upstream feature is OFF by default. Config `.features.json`: {"memory_search_fts":{"enabled":true}}. Normal query/rebuild refuses disabled feature with exit 2; --status allowed regardless.
- FTS5 availability tested by creating an in-memory virtual FTS5 table. If unavailable, query falls back to installed rg, then grep. If neither exists, search returns no results; --status identifies fallback unavailable.
- Absent index rebuilds on query. Stale detection checks memory file newer than DB; indexed filename now missing; operational error reading DB schema. Index explicitly rebuildable through --rebuild; unavailable FTS5 rebuild prints inability and returns.
- Indexable suffixes: .md/.jsonl, recursively under MEMORY_DIR; skips .index. Index stores filename/content and uses porter unicode61 tokenization. FTS MATCH ranking and snippets; invalid MATCH syntax falls back to LIKE. CJK no-result query attempts substring LIKE fallback.
- Important fidelity gap: `_read_jsonl` concatenates only action, reflection, detail, skill. Semantic `claim` and candidate claims are not included by this function. Candidate .json not indexed at all. Rendered LESSONS.md therefore matters for semantic recall with exact upstream implementation.
- Important invalidation edge: needs_rebuild compares indexed-current only, not current-indexed. A newly added file whose mtime is older than existing DB can remain unindexed until explicit rebuild/another change. Maintenance should explicitly invalidate/rebuild after rewrites rather than relying only on mtimes.
- Fallback scans text directly, so its matching behavior differs from structured JSONL FTS extraction. If rg/grep missing, upstream absence is indistinguishable from no match in ordinary query output; worth defining clearer availability behavior.
- No verified atomic index publication or interprocess index lock in this module. build_index drops and creates FTS table on same DB, inserts then commits. Concurrent maintenance/index queries remain a verification target.

Design implication: choose whether FTS remains opt-in for upstream fidelity or enabled by extraction defaults. Existing spec chooses FTS5 first but does not establish feature default. Prefer keep query-time derived-cache rebuild available while maintenance supports explicit rebuild; requiring maintenance before first recall differs from upstream.

## Existing auxiliary paths and root resolution

Upstream memory_search anchors root to Path(__file__).resolve().parent; .index/memory.db and .features.json live directly under that root. Upstream auto_dream uses script directory ROOT, candidates/ and working/REVIEW_QUEUE.md. Other tools build BASE from file positions and append memory/category paths.

Local core `ageroot_skills/skills/memory-manager/scripts/memory_manager.py`:44-58:
1. --memory-root
2. MEMORY_MANAGER_DATA_ROOT
3. --config JSON memory_root; relative values relative to config file
4. cwd/.agents/memory

Explicit CLI/env relative path resolved against cwd. No Git-root discovery in this resolver. No automatic config-file discovery: --config must be supplied.

Local reflection `scripts/memory_reflect.py`:26-28 accepts only --memory-root/env/cwd default; no --config support. One shared resolver is required for parity across the new runtime entry points, not currently established.

Local template `templates/memory-manager.config.json` contains {"memory_root":".agents/memory"}. If copied into .agents/ unchanged and passed --config, resolves .agents/.agents/memory; documentation must distinguish placement-relative paths from project-root-relative paths.

Accepted spec permits auxiliary state outside category dirs. Minimal upstream adaptation could retain candidates/, .index/, .features.json and place REVIEW_QUEUE.md outside removed working/, but no exact layout has been accepted. This is not a requirement to nest everything under semantic. Separate data-root and external preference resolution needed if data root is custom; inferring project preferences from arbitrary data-root parent is unreliable.

## Concurrency and interruption

Upstream auto_dream source:
https://github.com/codejunkie99/agentic-stack/blob/9424c58e1cfc17a709d1adfa13678e876edfe409/.agent/memory/auto_dream.py

- `_episodic_locked` opens active episodic JSONL and holds exclusive fcntl flock across entire load/cluster/stage/decay/rewrite/archive/queue window. Matching appenders must take same file lock; otherwise events appended after load can be truncated by rewrite.
- Rewrite is ftruncate(fd,0), seek to beginning, os.write payload. This lock prevents cooperating concurrent appends from racing, but does not make interruption between truncate and completed write recoverable. A partial os.write return is not retried in inspected function.
- Windows/no fcntl yields None and uses ordinary read/write fallback; upstream explicitly calls this best effort. No equivalent cross-platform lock guarantee.
- Existing local reflection acquires exclusive file flock around byte append + flush; no fsync. Existing core lifecycle json_line appends without flock. Thus existing local code does not provide a common journal-wide maintenance lock contract.
- Lock scope specifically protects episodic inode. Candidate files, semantic source/render and search DB are outside proven shared lock. Explicit maintenance alone does not imply all other sessions stopped.

Inference for design: shared root-level lock plus atomic temp-file replace/journal recovery could provide stronger cross-command coordination, but all writers must participate. Replacing an inode while appenders lock old active file can defeat a naive file-lock design; use stable lock path if atomic replace selected. POSIX-only initial support or portable locking mechanism remains a concrete choice. This report does not claim upstream already has these guarantees.

## Local legacy DECISIONS classification

Actual `.agents/memory/DECISIONS.md` was read this round: architecture decisions for Ageroot renderer/update model, accepted section plus open questions. It is semantic architectural knowledge, not episodic event log or personal preferences. Natural target is semantic/DECISIONS.md; do not convert its prose into episode rows or inferred accepted lesson claims.

Bounded rg across `.agents/ageroot.state.yaml`, `.agents/ageroot.config.yaml`, and `ageroot_template/.agents` found no DECISIONS path reference. This establishes no matching text there, not a guarantee no references exist anywhere in repository.

Migration can propose copy/import preserving bytes and source until explicit reviewed application. If target exists with different content, report conflict; do not merge architectural decisions mechanically. The file contains historical policy assertions; migration preserves it as data and does not turn its statements into new execution instructions. Nothing migrated this round.

## Known / unverified

Known: exact source FTS and auto_dream behavior above; current core/reflection root mismatch; current DECISIONS semantic classification. Unverified: actual SQLite FTS availability on target consumers, interruption outcomes under tests, other installations’ legacy data, whole-repository DECISIONS references, final CLI/path/lock contract.

Changed only this report. No tests, source edits, installs, migration, network requests or session-record access.
