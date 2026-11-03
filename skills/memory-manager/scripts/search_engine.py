"""Search subsystem with SQLite FTS5, query-time rebuild, and rg/grep fallback."""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

from common_resolver import ensure_memory_layout, read_jsonl

MEMORY_SUFFIXES = (".md", ".jsonl")
CJK_RE = re.compile(r"[\u3400-\u9fff]")


def feature_enabled(memory_root: Path) -> bool:
    features_path = memory_root / ".features.json"
    try:
        data = json.loads(features_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    entry = data.get("memory_search_fts") or {}
    return bool(entry.get("enabled"))


def check_fts5() -> bool:
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE VIRTUAL TABLE _t USING fts5(c)")
        conn.close()
        return True
    except Exception:
        return False


def _memory_files(memory_root: Path) -> list[Path]:
    files = []
    for p in memory_root.rglob("*"):
        if ".index" in p.parts:
            continue
        if p.suffix in MEMORY_SUFFIXES and p.is_file():
            files.append(p)
    return files


def _read_searchable_jsonl(path: Path) -> str:
    """Read a JSONL file and extract all searchable text, including claim and conditions."""
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
            parts = [
                entry.get("claim", ""),
                " ".join(entry.get("conditions", [])) if isinstance(entry.get("conditions"), list) else "",
                entry.get("action", ""),
                entry.get("reflection", ""),
                entry.get("detail", ""),
                entry.get("skill", ""),
                entry.get("rationale", ""),
                entry.get("notes", ""),
            ]
            text = " ".join(p for p in parts if p)
            if text:
                lines.append(text)
        except json.JSONDecodeError:
            continue
    return "\n".join(lines)


def _read_searchable_candidate_json(path: Path) -> str:
    try:
        entry = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        parts = [
            entry.get("claim", ""),
            " ".join(entry.get("conditions", [])) if isinstance(entry.get("conditions"), list) else "",
            entry.get("name", ""),
        ]
        return " ".join(p for p in parts if p)
    except Exception:
        return ""


def needs_rebuild(memory_root: Path) -> bool:
    index_path = memory_root / ".index" / "memory.db"
    if not index_path.exists():
        return True
    index_mtime = index_path.stat().st_mtime

    mem_files = _memory_files(memory_root)
    # Check candidate JSONs too
    candidates_dir = memory_root / "candidates"
    if candidates_dir.exists():
        for cand in candidates_dir.rglob("*.json"):
            if cand.is_file():
                mem_files.append(cand)

    current_rel = set()
    for f in mem_files:
        if f.stat().st_mtime > index_mtime:
            return True
        current_rel.add(str(f.relative_to(memory_root)))

    try:
        conn = sqlite3.connect(index_path)
        indexed_rel = {row[0] for row in conn.execute("SELECT filename FROM memories")}
        conn.close()
    except sqlite3.OperationalError:
        return True

    if indexed_rel != current_rel:
        return True
    return False


def build_index(memory_root: Path) -> int:
    index_dir = memory_root / ".index"
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / "memory.db"

    conn = sqlite3.connect(index_path)
    conn.execute("DROP TABLE IF EXISTS memories")
    conn.execute("""
        CREATE VIRTUAL TABLE memories
        USING fts5(filename, content, tokenize='porter unicode61')
    """)
    indexed = 0
    mem_files = _memory_files(memory_root)
    for f in mem_files:
        try:
            if f.suffix == ".md":
                content = f.read_text(encoding="utf-8", errors="replace")
            elif f.suffix == ".jsonl":
                content = _read_searchable_jsonl(f)
            else:
                continue
            rel_path = str(f.relative_to(memory_root))
            conn.execute("INSERT INTO memories VALUES (?, ?)", (rel_path, content))
            indexed += 1
        except Exception:
            pass

    # Also index candidate json files
    candidates_dir = memory_root / "candidates"
    if candidates_dir.exists():
        for f in candidates_dir.rglob("*.json"):
            if f.is_file():
                try:
                    content = _read_searchable_candidate_json(f)
                    if content:
                        rel_path = str(f.relative_to(memory_root))
                        conn.execute("INSERT INTO memories VALUES (?, ?)", (rel_path, content))
                        indexed += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()
    return indexed


def search_fts5(memory_root: Path, query: str) -> list[tuple[str, str]]:
    if needs_rebuild(memory_root):
        build_index(memory_root)
    index_path = memory_root / ".index" / "memory.db"
    conn = sqlite3.connect(index_path)
    try:
        rows = conn.execute(
            """SELECT filename,
                      snippet(memories, 1, '>>>', '<<<', '...', 30)
               FROM memories
               WHERE memories MATCH ?
               ORDER BY rank""",
            (query,),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = conn.execute(
            "SELECT filename, substr(content, 1, 300) FROM memories WHERE content LIKE ?",
            (f"%{query}%",),
        ).fetchall()

    if not rows and CJK_RE.search(query):
        rows = conn.execute(
            "SELECT filename, substr(content, 1, 300) FROM memories WHERE content LIKE ?",
            (f"%{query}%",),
        ).fetchall()
    conn.close()
    return [(str(row[0]), str(row[1])) for row in rows]


def _fallback_command(query: str, targets: list[str]) -> tuple[list[str] | None, str | None]:
    if shutil.which("rg"):
        return (["rg", "-li", "--", query, *targets], "ripgrep")
    if shutil.which("grep"):
        return (["grep", "-ril", query, *targets], "grep")
    return (None, None)


def fallback_tool() -> str:
    _, tool = _fallback_command("", [])
    return tool or "unavailable"


def search_fallback(memory_root: Path, query: str) -> list[tuple[str, str]]:
    targets = [str(f) for f in _memory_files(memory_root)]
    candidates_dir = memory_root / "candidates"
    if candidates_dir.exists():
        for cand in candidates_dir.rglob("*.json"):
            if cand.is_file():
                targets.append(str(cand))
    if not targets:
        return []
    cmd, _ = _fallback_command(query, targets)
    if not cmd:
        return []
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    files = [f for f in result.stdout.strip().split("\n") if f]
    matches = []
    for f in files:
        try:
            rel = Path(f).relative_to(memory_root)
            matches.append((str(rel), f"(match in {Path(f).name})"))
        except ValueError:
            matches.append((f, f"(match in {Path(f).name})"))
    return matches


def execute_search(memory_root: Path, query: str) -> tuple[list[tuple[str, str]], str]:
    if check_fts5():
        return search_fts5(memory_root, query), "FTS5"
    tool = fallback_tool()
    if tool == "unavailable":
        return [], "unavailable"
    return search_fallback(memory_root, query), tool
