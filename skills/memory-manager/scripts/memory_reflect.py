#!/usr/bin/env python3
"""Append one portable success or failure event to episodic memory with provenance."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common_resolver import (
    append_jsonl,
    get_consumer_commit_sha,
    now_iso,
    resolve_memory_root,
    root_lock,
)

FAILURE_THRESHOLD = 3
FAILURE_WINDOW_DAYS = 14


def recent_failures(path: Path, skill: str) -> int:
    if not path.exists():
        return 0
    import datetime as dt
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=FAILURE_WINDOW_DAYS)
    count = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            record = json.loads(raw)
            stamp = dt.datetime.fromisoformat(str(record.get("timestamp", "")).replace("Z", "+00:00"))
            stamp = stamp.replace(tzinfo=dt.timezone.utc) if stamp.tzinfo is None else stamp
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if record.get("skill") == skill and record.get("result") == "failure" and stamp > cutoff:
            count += 1
    return count


def parser() -> argparse.ArgumentParser:
    cmd = argparse.ArgumentParser(description=__doc__)
    cmd.add_argument("--memory-root", help="project-owned memory data root")
    cmd.add_argument("--config", help="JSON file containing memory_root")
    cmd.add_argument("skill")
    cmd.add_argument("action")
    cmd.add_argument("outcome")
    cmd.add_argument("--fail", action="store_true", help="record a failure")
    cmd.add_argument("--importance", type=int, default=None)
    cmd.add_argument("--note", default="", help="success reflection or failure context")
    cmd.add_argument("--confidence", type=float)
    cmd.add_argument("--evidence", nargs="*", default=[])
    cmd.add_argument("--pain", type=int)
    return cmd


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = resolve_memory_root(args.memory_root, args.config)
    episodic = root / "episodic" / "AGENT_LEARNINGS.jsonl"
    failure = args.fail
    reflection = args.note[:300]
    if failure:
        reflection = f"FAILURE in {args.skill}: {args.outcome[:200]}"
        if args.note:
            reflection += f" | context: {args.note[:300]}"

    record: dict[str, Any] = {
        "timestamp": now_iso(),
        "skill": args.skill,
        "action": args.action[:200],
        "result": "failure" if failure else "success",
        "detail": args.outcome[:500],
        "pain_score": args.pain if args.pain is not None else (8 if failure else 2),
        "importance": args.importance if args.importance is not None else (7 if failure else 5),
        "reflection": reflection,
        "confidence": args.confidence if args.confidence is not None else (0.9 if failure else 0.5),
        "source": {
            "skill": args.skill,
            "profile": os.environ.get("AGENT_PROFILE", "default"),
            "run_id": os.environ.get("AGENT_RUN_ID", f"pid-{os.getpid()}"),
            "commit_sha": get_consumer_commit_sha(root),
        },
        "evidence_ids": args.evidence or [],
    }

    with root_lock(root):
        if failure:
            record["context"] = args.note[:300]
            failures = recent_failures(episodic, args.skill) + 1
            if failures >= FAILURE_THRESHOLD:
                record["reflection"] += f" | THIS SKILL HAS FAILED {failures} TIMES IN {FAILURE_WINDOW_DAYS}d. Flag for rewrite."
                record["pain_score"] = 10
        append_jsonl(episodic, record)

    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
