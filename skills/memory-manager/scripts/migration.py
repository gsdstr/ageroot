"""Legacy memory migration preview and apply."""
from __future__ import annotations

import filecmp
import json
import shutil
from pathlib import Path
from typing import Any

from common_resolver import ensure_memory_layout, root_lock


def detect_legacy_layout(source_root: Path) -> dict[str, Any]:
    """Inspect source_root for legacy memory files and layouts."""
    recognized: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    unknown: list[str] = []

    if not source_root.exists():
        return {
            "source_root": str(source_root),
            "recognized": [],
            "conflicts": [],
            "unknown": [],
            "total_items": 0,
        }

    # 1. Check legacy DECISIONS.md at root of source_root
    legacy_decisions = source_root / "DECISIONS.md"
    if legacy_decisions.is_file():
        target = source_root / "semantic" / "DECISIONS.md"
        status = "ready"
        if target.exists():
            if filecmp.cmp(legacy_decisions, target, shallow=False):
                status = "identical"
            else:
                status = "conflict"
        item = {
            "source": str(legacy_decisions.relative_to(source_root)),
            "target": "semantic/DECISIONS.md",
            "type": "markdown_decisions",
            "status": status,
        }
        if status == "conflict":
            conflicts.append(item)
        else:
            recognized.append(item)

    # 2. Check legacy LESSONS.md at root of source_root
    legacy_lessons = source_root / "LESSONS.md"
    if legacy_lessons.is_file():
        target = source_root / "semantic" / "LESSONS.md"
        status = "ready"
        if target.exists():
            if filecmp.cmp(legacy_lessons, target, shallow=False):
                status = "identical"
            else:
                status = "conflict"
        item = {
            "source": str(legacy_lessons.relative_to(source_root)),
            "target": "semantic/LESSONS.md",
            "type": "markdown_lessons",
            "status": status,
        }
        if status == "conflict":
            conflicts.append(item)
        else:
            recognized.append(item)

    # 3. Check legacy episodic files in source_root
    legacy_episodic = source_root / "AGENT_LEARNINGS.jsonl"
    if legacy_episodic.is_file():
        target = source_root / "episodic" / "AGENT_LEARNINGS.jsonl"
        status = "ready"
        if target.exists():
            if filecmp.cmp(legacy_episodic, target, shallow=False):
                status = "identical"
            else:
                status = "mergeable"
        recognized.append({
            "source": str(legacy_episodic.relative_to(source_root)),
            "target": "episodic/AGENT_LEARNINGS.jsonl",
            "type": "episodic_jsonl",
            "status": status,
        })

    # 4. Check for unknown files at top level
    for child in source_root.iterdir():
        if child.name in (
            "episodic", "semantic", "candidates", ".index", ".features.json",
            ".lock", "REVIEW_QUEUE.md", "DECISIONS.md", "LESSONS.md", "AGENT_LEARNINGS.jsonl"
        ):
            continue
        unknown.append(str(child.relative_to(source_root)))

    return {
        "source_root": str(source_root),
        "recognized": recognized,
        "conflicts": conflicts,
        "unknown": unknown,
        "total_items": len(recognized) + len(conflicts),
    }


def preview_migration(memory_root: Path) -> dict[str, Any]:
    return detect_legacy_layout(memory_root)


def apply_migration(memory_root: Path) -> dict[str, Any]:
    with root_lock(memory_root):
        ensure_memory_layout(memory_root)
        plan = detect_legacy_layout(memory_root)
        if plan["conflicts"]:
            raise ValueError(f"cannot apply migration with conflicts: {plan['conflicts']}")

        migrated = []
        for item in plan["recognized"]:
            src = memory_root / item["source"]
            dst = memory_root / item["target"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            if item["type"] in ("markdown_decisions", "markdown_lessons"):
                if item["status"] == "ready":
                    shutil.copy2(src, dst)
                    migrated.append(item)
                elif item["status"] == "identical":
                    migrated.append(item)
            elif item["type"] == "episodic_jsonl":
                if item["status"] == "ready":
                    shutil.copy2(src, dst)
                    migrated.append(item)
                elif item["status"] == "mergeable":
                    # Source preserving, append distinct records
                    existing_lines = set(dst.read_text(encoding="utf-8").splitlines()) if dst.exists() else set()
                    with dst.open("a", encoding="utf-8") as out:
                        for line in src.read_text(encoding="utf-8").splitlines():
                            if line.strip() and line not in existing_lines:
                                out.write(line + "\n")
                                existing_lines.add(line)
                    migrated.append(item)
                elif item["status"] == "identical":
                    migrated.append(item)

        return {
            "status": "applied",
            "migrated": migrated,
            "conflicts": plan["conflicts"],
            "unknown": plan["unknown"],
        }
