#!/usr/bin/env python3
"""Memory maintenance CLI: clustering, candidate staging, decay/archive, review queue update, and FTS rebuild."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

# Resolve manager runtime dependency
HERE = Path(__file__).resolve()
DEFAULT_MANAGER_SCRIPTS = [
    HERE.parents[2] / "memory-manager" / "scripts",
    Path.cwd() / ".agents" / "skills" / "memory-manager" / "scripts",
]


def find_manager_runtime(explicit_path: str | None = None) -> Path:
    if explicit_path:
        p = Path(explicit_path).expanduser().resolve()
        if (p / "common_resolver.py").is_file():
            return p
        if (p / "scripts" / "common_resolver.py").is_file():
            return p / "scripts"
        raise ValueError(f"incompatible or missing memory-manager runtime at {explicit_path}")

    env_mgr = os.environ.get("MEMORY_MANAGER_RUNTIME")
    if env_mgr:
        p = Path(env_mgr).expanduser().resolve()
        if (p / "common_resolver.py").is_file():
            return p
        if (p / "scripts" / "common_resolver.py").is_file():
            return p / "scripts"

    for candidate in DEFAULT_MANAGER_SCRIPTS:
        cand_res = candidate.resolve()
        if (cand_res / "common_resolver.py").is_file():
            return cand_res

    raise RuntimeError(
        "memory-maintenance requires memory-manager runtime, but it was not found. "
        "Install memory-manager or specify --manager-runtime <path> / MEMORY_MANAGER_RUNTIME."
    )


def verify_runtime_compatibility(manager_scripts_dir: Path) -> None:
    if str(manager_scripts_dir) not in sys.path:
        sys.path.insert(0, str(manager_scripts_dir))
    try:
        import common_resolver
        api_ver = getattr(common_resolver, "RUNTIME_API_VERSION", None)
        if api_ver != 1:
            raise ValueError(f"incompatible memory-manager runtime API version (expected 1, got {api_ver})")
    except ImportError as exc:
        raise RuntimeError(f"failed to import memory-manager runtime from {manager_scripts_dir}: {exc}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory-root", help="project-owned memory data root")
    parser.add_argument("--config", help="JSON file containing memory_root")
    parser.add_argument("--manager-runtime", help="path to memory-manager scripts directory")
    parser.add_argument("--cluster-threshold", type=float, default=0.3)
    parser.add_argument("--promotion-threshold", type=float, default=7.0)
    parser.add_argument("--decay-days", type=int, default=90)
    parser.add_argument("--salience-floor", type=float, default=2.0)
    parser.add_argument("--lock-timeout", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true", help="preview maintenance actions without applying changes")
    return parser.parse_args(argv)


def run_maintenance(
    memory_root: Path,
    manager_scripts: Path,
    cluster_threshold: float = 0.3,
    promotion_threshold: float = 7.0,
    decay_days: int = 90,
    salience_floor: float = 2.0,
    lock_timeout: float = 5.0,
    dry_run: bool = False,
) -> dict[str, Any]:
    if str(manager_scripts) not in sys.path:
        sys.path.insert(0, str(manager_scripts))

    upstream_mem = manager_scripts / "upstream" / "memory"
    upstream_tools = manager_scripts / "upstream" / "tools"
    upstream_harness = manager_scripts / "upstream" / "harness"
    for p in (upstream_mem, upstream_tools, upstream_harness):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))

    from common_resolver import ensure_memory_layout, root_lock, read_jsonl, safe_atomic_replace, now_iso
    from promote import cluster_and_extract, write_candidates
    from validate import heuristic_check
    from review_state import mark_rejected, write_review_queue_summary
    from decay import decay_old_entries
    from search_engine import build_index

    candidates_dir = memory_root / "candidates"
    semantic_dir = memory_root / "semantic"
    episodic_path = memory_root / "episodic" / "AGENT_LEARNINGS.jsonl"
    archive_dir = memory_root / "episodic" / "snapshots"
    review_queue_path = memory_root / "REVIEW_QUEUE.md"

    with root_lock(memory_root, timeout=lock_timeout):
        ensure_memory_layout(memory_root)

        entries = read_jsonl(episodic_path) if episodic_path.exists() else []

        patterns = cluster_and_extract(entries, threshold=cluster_threshold) if entries else {}
        promotable = {k: p for k, p in patterns.items() if p.get("canonical_salience", 0) >= promotion_threshold}

        if dry_run:
            return {
                "dry_run": True,
                "patterns": len(patterns),
                "staged": len(promotable),
                "prefiltered_out": 0,
                "pending_review": 0,
                "archived_episodes": sum(1 for e in entries if float(e.get("salience", e.get("importance", 1))) < salience_floor),
                "kept_episodes": len(entries),
                "indexed_files": 0,
            }

        # 1. Write staged candidates
        staged = write_candidates(promotable, str(candidates_dir))

        # 2. Heuristic prefilter junk
        lessons_md_path = semantic_dir / "LESSONS.md"
        existing_lessons = lessons_md_path.read_text(encoding="utf-8") if lessons_md_path.exists() else ""
        prefiltered = 0
        if candidates_dir.is_dir():
            for fpath in sorted(candidates_dir.glob("*.json")):
                if not fpath.is_file() or fpath.name == "events.jsonl":
                    continue
                try:
                    cand = json.loads(fpath.read_text(encoding="utf-8"))
                    chk = heuristic_check(cand, existing_lessons)
                    if not chk["passed"]:
                        reason = ", ".join(chk["reasons"])
                        mark_rejected(
                            cand["id"], "heuristic_prefilter", reason, str(candidates_dir),
                            duplicate_claims=chk.get("duplicates", [])
                        )
                        prefiltered += 1
                except Exception:
                    pass

        # 3. Decay & Archive old low-salience entries
        kept, archived = decay_old_entries(entries, archive_dir=str(archive_dir))
        if len(archived) > 0:
            # Atomic rewrite of episodic journal
            payload = ("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in kept)).encode("utf-8")
            safe_atomic_replace(episodic_path, payload)

        # 4. Refresh review queue summary at memory root
        pending = write_review_queue_summary(str(candidates_dir), str(review_queue_path))

        # 5. Rebuild FTS5 index
        indexed_files = build_index(memory_root)

        return {
            "status": "success",
            "dry_run": False,
            "patterns": len(patterns),
            "staged": staged,
            "prefiltered_out": prefiltered,
            "pending_review": pending,
            "archived_episodes": len(archived),
            "kept_episodes": len(kept),
            "indexed_files": indexed_files,
        }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manager_scripts = find_manager_runtime(args.manager_runtime)
        verify_runtime_compatibility(manager_scripts)

        if str(manager_scripts) not in sys.path:
            sys.path.insert(0, str(manager_scripts))
        from common_resolver import resolve_memory_root

        root = resolve_memory_root(args.memory_root, args.config)
        result = run_maintenance(
            memory_root=root,
            manager_scripts=manager_scripts,
            cluster_threshold=args.cluster_threshold,
            promotion_threshold=args.promotion_threshold,
            decay_days=args.decay_days,
            salience_floor=args.salience_floor,
            lock_timeout=args.lock_timeout,
            dry_run=args.dry_run,
        )
        print(
            f"maintenance: patterns={result.get('patterns', 0)} "
            f"staged={result.get('staged', 0)} "
            f"prefiltered_out={result.get('prefiltered_out', 0)} "
            f"pending_review={result.get('pending_review', 0)} "
            f"archived={result.get('archived_episodes', 0)} "
            f"kept={result.get('kept_episodes', 0)} "
            f"indexed={result.get('indexed_files', 0)}"
        )
        return 0
    except (RuntimeError, ValueError, OSError, TimeoutError) as exc:
        print(f"memory-maintenance: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
