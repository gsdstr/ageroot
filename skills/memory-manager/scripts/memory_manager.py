#!/usr/bin/env python3
"""Portable memory lifecycle manager CLI. Python standard library only."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Upstream modules path
UPSTREAM_MEM = SCRIPTS_DIR / "upstream" / "memory"
UPSTREAM_TOOLS = SCRIPTS_DIR / "upstream" / "tools"
UPSTREAM_HARNESS = SCRIPTS_DIR / "upstream" / "harness"

for p in (UPSTREAM_MEM, UPSTREAM_TOOLS, UPSTREAM_HARNESS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from common_resolver import (
    RUNTIME_API_VERSION,
    SENTINEL,
    append_jsonl,
    ensure_memory_layout,
    now_iso,
    read_jsonl,
    resolve_memory_root,
    resolve_preferences_path,
    root_lock,
    safe_atomic_replace,
)
from migration import apply_migration, preview_migration
from search_engine import build_index, execute_search, feature_enabled, check_fts5, fallback_tool


def candidates_dir(root: Path) -> Path:
    return root / "candidates"


def candidate_path(root: Path, candidate_id: str) -> Path:
    if Path(candidate_id).name != candidate_id or not candidate_id:
        raise ValueError("candidate id must be a plain filename")
    return candidates_dir(root) / f"{candidate_id}.json"


def load_candidate(root: Path, candidate_id: str) -> dict[str, Any]:
    # Check staged, graduated, and rejected dirs
    for check_dir in (candidates_dir(root), candidates_dir(root) / "graduated", candidates_dir(root) / "rejected"):
        p = check_dir / f"{candidate_id}.json"
        if p.is_file():
            try:
                val = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(val, dict):
                    return val
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid candidate record: {p}") from exc
    raise ValueError(f"candidate not found: {candidate_id}")


def events(root: Path) -> list[dict[str, Any]]:
    return read_jsonl(candidates_dir(root) / "events.jsonl")


def candidate_state(root: Path, candidate_id: str) -> str:
    # First check lifecycle subdir
    if (candidates_dir(root) / "graduated" / f"{candidate_id}.json").is_file():
        return "graduated"
    if (candidates_dir(root) / "rejected" / f"{candidate_id}.json").is_file():
        return "rejected"
    if (candidates_dir(root) / f"{candidate_id}.json").is_file():
        state = "staged"
        for event in events(root):
            if event.get("candidate_id") == candidate_id:
                state = str(event.get("action", state))
        return state
    return "unknown"


def append_event(root: Path, candidate_id: str, action: str, reviewer: str, notes: str) -> None:
    append_jsonl(candidates_dir(root) / "events.jsonl", {
        "ts": now_iso(), "candidate_id": candidate_id, "action": action,
        "reviewer": reviewer, "notes": notes,
    })


def latest_by_id(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id:
            latest[record_id] = record
    return latest


def cmd_stage(root: Path, args: argparse.Namespace) -> int:
    claim = args.claim.strip()
    if not claim:
        raise ValueError("claim must not be empty")
    candidate_id = args.id or hashlib.sha256(claim.encode("utf-8")).hexdigest()[:12]
    path = candidate_path(root, candidate_id)

    with root_lock(root):
        ensure_memory_layout(root)
        if path.exists() or (candidates_dir(root) / "graduated" / f"{candidate_id}.json").exists():
            raise ValueError(f"candidate already exists: {candidate_id}")
        candidate = {
            "id": candidate_id,
            "claim": claim,
            "conditions": args.condition or [],
            "evidence_ids": args.evidence or [],
            "staged_at": now_iso(),
            "reviewer": args.reviewer,
            "status": "staged",
            "schema": "memory-manager/candidate-v1",
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        append_event(root, candidate_id, "staged", args.reviewer, "candidate recorded")

    print(candidate_id)
    return 0


def cmd_list(root: Path, _: argparse.Namespace) -> int:
    ensure_memory_layout(root)
    # Staged
    for path in sorted(candidates_dir(root).glob("*.json")):
        if path.name == "events.jsonl":
            continue
        try:
            cand = json.loads(path.read_text(encoding="utf-8"))
            cid = cand.get("id", path.stem)
            print(f"{cid}\t{candidate_state(root, str(cid))}\t{cand.get('claim', '')}")
        except Exception:
            pass
    # Graduated
    for path in sorted((candidates_dir(root) / "graduated").glob("*.json")):
        try:
            cand = json.loads(path.read_text(encoding="utf-8"))
            cid = cand.get("id", path.stem)
            print(f"{cid}\tgraduated\t{cand.get('claim', '')}")
        except Exception:
            pass
    # Rejected
    for path in sorted((candidates_dir(root) / "rejected").glob("*.json")):
        try:
            cand = json.loads(path.read_text(encoding="utf-8"))
            cid = cand.get("id", path.stem)
            print(f"{cid}\trejected\t{cand.get('claim', '')}")
        except Exception:
            pass
    return 0


def cmd_search(root: Path, args: argparse.Namespace) -> int:
    ensure_memory_layout(root)
    results, mode = execute_search(root, args.query)
    if mode == "unavailable" and not results:
        print(f"Search unavailable: FTS5 and fallback tools (rg/grep) not available.", file=sys.stderr)
        return 1
    if not results:
        print(f"No results for: '{args.query}'  [mode: {mode}]")
        return 0
    print(f"Results for: '{args.query}'  [mode: {mode}]\n")
    for filename, snippet in results:
        print(f"  {filename}")
        print(f"  {snippet}\n")
    return 0


def cmd_recall(root: Path, args: argparse.Namespace) -> int:
    ensure_memory_layout(root)
    semantic_dir = root / "semantic"
    lessons_jsonl = semantic_dir / "lessons.jsonl"
    lessons_md = semantic_dir / "LESSONS.md"

    # Load lessons from semantic
    rows = read_jsonl(lessons_jsonl) if lessons_jsonl.exists() else []
    latest = latest_by_id(rows)

    from render_lessons import superseded_by_map
    retired = superseded_by_map(latest.values())
    active_lessons = [l for lid, l in latest.items() if lid not in retired and l.get("status") in ("accepted", "legacy")]

    from text import word_set
    qwords = word_set(args.intent)

    def score_lesson(l: dict[str, Any]) -> float:
        if not qwords:
            return 0.0
        cwords = word_set(l.get("claim", ""))
        condwords = set()
        for c in l.get("conditions", []) or []:
            condwords |= word_set(c)
        chits = len(qwords & cwords)
        condhits = len(qwords & condwords)
        raw = chits + 2 * condhits
        max_raw = 3 * len(qwords)
        return raw / max_raw if max_raw else 0.0

    scored = []
    for l in active_lessons:
        s = score_lesson(l)
        if s > 0.01:
            scored.append((s, l))
    scored.sort(key=lambda x: -x[0])

    top = scored[:args.top]
    if args.json:
        out = [{"id": l.get("id"), "claim": l.get("claim"), "score": round(s, 3)} for s, l in top]
        print(json.dumps(out, indent=2))
    else:
        print(f"Consulted lessons for intent: {args.intent!r}")
        if not top:
            print("  -> no relevant lessons.")
        for i, (s, l) in enumerate(top, 1):
            print(f"  [{i}] score={s:.3f}  {l.get('claim')}  [id={l.get('id')}]")
    return 0


def cmd_accept(root: Path, args: argparse.Namespace) -> int:
    with root_lock(root):
        ensure_memory_layout(root)
        candidate = load_candidate(root, args.candidate_id)
        current_st = candidate_state(root, args.candidate_id)
        if current_st != "staged":
            raise ValueError(f"only staged candidates can be accepted (current: {current_st})")

        lesson_id = f"lesson_{args.candidate_id}"
        semantic_dir = root / "semantic"
        semantic_jsonl = semantic_dir / "lessons.jsonl"
        latest = latest_by_id(read_jsonl(semantic_jsonl))
        if lesson_id in latest and latest[lesson_id].get("status") == "accepted":
            raise ValueError(f"lesson already exists: {lesson_id}")

        lesson = {
            "id": lesson_id,
            "claim": candidate.get("claim", ""),
            "conditions": candidate.get("conditions", []),
            "evidence_ids": candidate.get("evidence_ids", []),
            "status": "provisional" if args.provisional else "accepted",
            "accepted_at": now_iso(),
            "reviewer": args.reviewer,
            "rationale": args.rationale,
            "source_candidate": args.candidate_id,
        }
        # Append-only write to semantic journal
        append_jsonl(semantic_jsonl, lesson)

        # Move candidate file to graduated/
        src_path = candidates_dir(root) / f"{args.candidate_id}.json"
        grad_dir = candidates_dir(root) / "graduated"
        grad_dir.mkdir(parents=True, exist_ok=True)
        dst_path = grad_dir / f"{args.candidate_id}.json"

        candidate["status"] = "provisional" if args.provisional else "accepted"
        candidate["accepted_at"] = now_iso()
        candidate["reviewer"] = args.reviewer
        candidate["rationale"] = args.rationale
        dst_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if src_path.exists():
            src_path.unlink()

        append_event(root, args.candidate_id, "accepted", args.reviewer, args.rationale)

        # Auto-render LESSONS.md projection
        cmd_render(root, argparse.Namespace(adopt_existing=True))

    print(lesson_id)
    return 0


def cmd_reject(root: Path, args: argparse.Namespace) -> int:
    with root_lock(root):
        ensure_memory_layout(root)
        candidate = load_candidate(root, args.candidate_id)
        current_st = candidate_state(root, args.candidate_id)
        if current_st != "staged":
            raise ValueError(f"only staged candidates can be rejected (current: {current_st})")

        src_path = candidates_dir(root) / f"{args.candidate_id}.json"
        rej_dir = candidates_dir(root) / "rejected"
        rej_dir.mkdir(parents=True, exist_ok=True)
        dst_path = rej_dir / f"{args.candidate_id}.json"

        candidate["status"] = "rejected"
        candidate["rejection_count"] = candidate.get("rejection_count", 0) + 1
        candidate["reviewer"] = args.reviewer
        candidate["reject_reason"] = args.reason
        dst_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if src_path.exists():
            src_path.unlink()

        append_event(root, args.candidate_id, "rejected", args.reviewer, args.reason)
    return 0


def cmd_reopen(root: Path, args: argparse.Namespace) -> int:
    with root_lock(root):
        ensure_memory_layout(root)
        candidate = load_candidate(root, args.candidate_id)
        current_st = candidate_state(root, args.candidate_id)
        if current_st != "rejected":
            raise ValueError(f"only rejected candidates can be reopened (current: {current_st})")

        rej_path = candidates_dir(root) / "rejected" / f"{args.candidate_id}.json"
        staged_path = candidates_dir(root) / f"{args.candidate_id}.json"

        candidate["status"] = "staged"
        staged_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if rej_path.exists():
            rej_path.unlink()

        append_event(root, args.candidate_id, "staged", args.reviewer, "reopened for review")
    return 0


def cmd_retract(root: Path, args: argparse.Namespace) -> int:
    with root_lock(root):
        ensure_memory_layout(root)
        semantic_dir = root / "semantic"
        semantic_jsonl = semantic_dir / "lessons.jsonl"
        latest = latest_by_id(read_jsonl(semantic_jsonl))
        lesson = latest.get(args.lesson_id)
        if lesson is None:
            raise ValueError(f"lesson not found: {args.lesson_id}")
        if lesson.get("status") not in ("accepted", "provisional", "legacy"):
            raise ValueError(f"only active lessons can be retracted (current: {lesson.get('status')})")

        retraction = dict(lesson)
        retraction.update({
            "status": "retracted",
            "retracted_at": now_iso(),
            "reviewer": args.reviewer,
            "rationale": args.rationale,
            "retracts": args.lesson_id,
        })
        append_jsonl(semantic_jsonl, retraction)
        # Re-render LESSONS.md projection
        cmd_render(root, argparse.Namespace(adopt_existing=True))
    return 0


def cmd_render(root: Path, args: argparse.Namespace) -> int:
    semantic_dir = root / "semantic"
    output = semantic_dir / "LESSONS.md"
    existing = output.read_text(encoding="utf-8") if output.exists() else "# Lessons\n"

    sentinel_to_use = SENTINEL
    if SENTINEL not in existing:
        # Check upstream sentinel
        upstream_sentinel = "## Auto-promoted entries will be appended below"
        if upstream_sentinel in existing:
            sentinel_to_use = upstream_sentinel
            prefix = existing.split(upstream_sentinel, 1)[0].rstrip()
        else:
            if output.exists() and not getattr(args, "adopt_existing", False):
                raise ValueError(f"{output} has no managed sentinel; use --adopt-existing to preserve it as preamble")
            prefix = existing.rstrip()
    else:
        prefix = existing.split(SENTINEL, 1)[0].rstrip()

    latest = latest_by_id(read_jsonl(semantic_dir / "lessons.jsonl"))

    from render_lessons import superseded_by_map
    retired = superseded_by_map(latest.values())

    lines = ["## Managed lessons", ""]
    active = [v for lid, v in latest.items() if lid not in retired and v.get("status") in ("accepted", "provisional", "legacy")]
    if not active:
        lines.append("_No accepted lessons._")
    for lesson in active:
        marker = " [PROVISIONAL]" if lesson.get("status") == "provisional" else ""
        lines.append(f"- {lesson.get('claim', '').strip()}{marker}  <!-- status={lesson.get('status')} id={lesson.get('id')} -->")

    rendered_text = f"{prefix}\n\n{SENTINEL}\n\n" + "\n".join(lines) + "\n"
    safe_atomic_replace(output, rendered_text.encode("utf-8"))
    print(output)
    return 0


def cmd_rebuild_index(root: Path, _: argparse.Namespace) -> int:
    with root_lock(root):
        ensure_memory_layout(root)
        count = build_index(root)
        print(f"Index rebuilt: {count} files indexed.")
    return 0


def cmd_migration_preview(root: Path, _: argparse.Namespace) -> int:
    res = preview_migration(root)
    print(json.dumps(res, indent=2))
    return 0


def cmd_migration_apply(root: Path, _: argparse.Namespace) -> int:
    res = apply_migration(root)
    print(json.dumps(res, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--memory-root", help="project-owned memory data root")
    p.add_argument("--config", help="JSON file containing memory_root")
    sub = p.add_subparsers(dest="command", required=True)

    # Stage
    stage = sub.add_parser("stage", help="stage a memory candidate")
    stage.add_argument("--claim", required=True)
    stage.add_argument("--id")
    stage.add_argument("--condition", action="append")
    stage.add_argument("--evidence", action="append")
    stage.add_argument("--reviewer", required=True)
    stage.set_defaults(handler=cmd_stage)

    # List
    sub.add_parser("list", help="list candidates").set_defaults(handler=cmd_list)

    # Search
    search = sub.add_parser("search", help="keyword search across memory")
    search.add_argument("query")
    search.set_defaults(handler=cmd_search)

    # Recall
    recall = sub.add_parser("recall", help="intent-based lesson recall")
    recall.add_argument("intent")
    recall.add_argument("--top", type=int, default=3)
    recall.add_argument("--json", action="store_true")
    recall.set_defaults(handler=cmd_recall)

    # Accept
    accept = sub.add_parser("accept", help="accept candidate into semantic lessons")
    accept.add_argument("candidate_id")
    accept.add_argument("--reviewer", required=True)
    accept.add_argument("--rationale", required=True)
    accept.add_argument("--provisional", action="store_true")
    accept.set_defaults(handler=cmd_accept)

    # Reject
    reject = sub.add_parser("reject", help="reject candidate")
    reject.add_argument("candidate_id")
    reject.add_argument("--reviewer", required=True)
    reject.add_argument("--reason", required=True)
    reject.set_defaults(handler=cmd_reject)

    # Reopen
    reopen = sub.add_parser("reopen", help="reopen rejected candidate")
    reopen.add_argument("candidate_id")
    reopen.add_argument("--reviewer", required=True)
    reopen.set_defaults(handler=cmd_reopen)

    # Retract
    retract = sub.add_parser("retract", help="retract accepted lesson")
    retract.add_argument("lesson_id")
    retract.add_argument("--reviewer", required=True)
    retract.add_argument("--rationale", required=True)
    retract.set_defaults(handler=cmd_retract)

    # Render
    render = sub.add_parser("render", help="render LESSONS.md projection")
    render.add_argument("--adopt-existing", action="store_true")
    render.set_defaults(handler=cmd_render)

    # Rebuild index
    rebuild = sub.add_parser("rebuild-index", help="rebuild search FTS5 index")
    rebuild.set_defaults(handler=cmd_rebuild_index)

    # Migration
    mig_prev = sub.add_parser("migrate-preview", help="preview legacy memory migration")
    mig_prev.set_defaults(handler=cmd_migration_preview)

    mig_apply = sub.add_parser("migrate-apply", help="apply legacy memory migration")
    mig_apply.set_defaults(handler=cmd_migration_apply)

    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = resolve_memory_root(args.memory_root, args.config)
        return args.handler(root, args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, TimeoutError) as error:
        print(f"memory-manager: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
