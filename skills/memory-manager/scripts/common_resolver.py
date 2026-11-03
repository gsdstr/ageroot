"""Shared project/data root resolver, bounded root lock, and memory runtime helpers."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
    _HAS_FCNTL = True
except ImportError:
    fcntl = None
    _HAS_FCNTL = False

RUNTIME_API_VERSION = 1
DEFAULT_LOCK_TIMEOUT_SECONDS = 5.0
SENTINEL = "<!-- memory-manager:generated -->"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def resolve_memory_root(
    args_memory_root: str | None = None,
    args_config: str | None = None,
    base_dir: Path | None = None,
) -> Path:
    """
    Priority:
    1. --memory-root
    2. MEMORY_MANAGER_DATA_ROOT
    3. --config (JSON file containing memory_root)
    4. <project-root>/.agents/memory
    """
    cwd = (base_dir or Path.cwd()).resolve()

    # 1. --memory-root
    if args_memory_root:
        p = Path(args_memory_root).expanduser()
        return (cwd / p).resolve() if not p.is_absolute() else p.resolve()

    # 2. MEMORY_MANAGER_DATA_ROOT
    env_root = os.environ.get("MEMORY_MANAGER_DATA_ROOT")
    if env_root:
        p = Path(env_root).expanduser()
        return (cwd / p).resolve() if not p.is_absolute() else p.resolve()

    # 3. --config
    if args_config:
        config_path = Path(args_config).expanduser()
        config_resolved = (cwd / config_path).resolve() if not config_path.is_absolute() else config_path.resolve()
        if not config_resolved.exists():
            raise ValueError(f"config file not found: {config_resolved}")
        try:
            config_data = json.loads(config_resolved.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in config {config_resolved}: {exc}") from exc
        if not isinstance(config_data, dict):
            raise ValueError(f"{config_resolved}: configuration must be a JSON object")
        configured = config_data.get("memory_root")
        if not isinstance(configured, str) or not configured.strip():
            raise ValueError(f"{config_resolved}: memory_root must be a non-empty string")
        p = Path(configured).expanduser()
        return (config_resolved.parent / p).resolve() if not p.is_absolute() else p.resolve()

    # 4. <project-root>/.agents/memory
    # Search upwards from cwd for .agents directory or git root
    curr = cwd
    project_root = None
    while True:
        if (curr / ".agents").is_dir() or (curr / ".git").exists():
            project_root = curr
            break
        if curr.parent == curr:
            break
        curr = curr.parent

    if project_root is None:
        project_root = cwd

    return (project_root / ".agents" / "memory").resolve()


def resolve_preferences_path(project_root_or_memory_root: Path) -> Path:
    """Preferences always resolve separately to <project-root>/.agents/PREFERENCES.md."""
    curr = project_root_or_memory_root.resolve()
    # If passed memory root (.agents/memory or custom), find parent project
    while True:
        if (curr / ".agents" / "PREFERENCES.md").exists() or (curr / ".agents").is_dir() or (curr / ".git").exists():
            return (curr / ".agents" / "PREFERENCES.md").resolve()
        if curr.parent == curr:
            break
        curr = curr.parent
    return (project_root_or_memory_root.resolve() / ".agents" / "PREFERENCES.md").resolve()


def ensure_memory_layout(root: Path, enable_fts_default: bool = True) -> None:
    """Ensure standard directory structure exists under memory root."""
    (root / "episodic").mkdir(parents=True, exist_ok=True)
    (root / "semantic").mkdir(parents=True, exist_ok=True)
    (root / "candidates").mkdir(parents=True, exist_ok=True)
    (root / "candidates" / "graduated").mkdir(parents=True, exist_ok=True)
    (root / "candidates" / "rejected").mkdir(parents=True, exist_ok=True)
    (root / ".index").mkdir(parents=True, exist_ok=True)

    features_file = root / ".features.json"
    if not features_file.exists() and enable_fts_default:
        features_file.write_text(
            json.dumps({"memory_search_fts": {"enabled": True}}, indent=2) + "\n",
            encoding="utf-8",
        )


@contextlib.contextmanager
def root_lock(root: Path, timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS) -> Iterator[None]:
    """
    Stable bounded-time root lock using root / '.lock'.
    Coordinates all concurrent workflow appenders and maintenance operations.
    """
    root.mkdir(parents=True, exist_ok=True)
    lock_file = root / ".lock"
    fd = os.open(str(lock_file), os.O_RDWR | os.O_CREAT, 0o644)
    start_time = time.time()
    acquired = False
    try:
        while True:
            if _HAS_FCNTL and fcntl is not None:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                    break
                except (BlockingIOError, OSError):
                    pass
            else:
                # Non-posix fallback
                acquired = True
                break

            if (time.time() - start_time) >= timeout:
                raise TimeoutError(f"could not acquire memory root lock at {lock_file} after {timeout:.1f}s")
            time.sleep(0.05)

        yield
    finally:
        if acquired and _HAS_FCNTL and fcntl is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        try:
            os.close(fd)
        except OSError:
            pass


def safe_atomic_replace(target_path: Path, content_bytes: bytes) -> None:
    """Crash-safe write using temp file and atomic os.replace."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.parent / f".tmp_{target_path.name}_{os.getpid()}_{time.time_ns()}"
    try:
        with open(tmp_path, "wb") as f:
            f.write(content_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSONL at {path}:{number}: {error.msg}") from error
        if not isinstance(record, dict):
            raise ValueError(f"invalid JSONL object at {path}:{number}")
        records.append(record)
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    payload = (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab") as stream:
        if _HAS_FCNTL and fcntl is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            stream.write(payload)
            stream.flush()
        finally:
            if _HAS_FCNTL and fcntl is not None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def get_consumer_commit_sha(memory_root: Path) -> str:
    """Find git commit SHA of consumer repo, without attributing skill repo."""
    try:
        # Search upwards for .git from memory root
        curr = memory_root.resolve()
        while True:
            if (curr / ".git").exists():
                res = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=curr,
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
                return res.stdout.strip() if res.returncode == 0 else ""
            if curr.parent == curr:
                break
            curr = curr.parent
        return ""
    except Exception:
        return ""
