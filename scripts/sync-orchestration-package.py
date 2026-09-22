#!/usr/bin/env python3
"""Check or explicitly mirror the portable orchestration package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "templates" / "orchestration" / "v1"
DEFAULT_TARGET = REPO_ROOT / "ageroot_template" / ".agents" / "orchestration"


def source_files(source_root: Path) -> dict[Path, bytes]:
    files = [
        source_root / "manifest.yaml",
        source_root / "README.md",
        source_root / "lifecycle-map.md",
        source_root / "scripts" / "validate.py",
    ]
    files.extend(sorted((source_root / "phases").glob("*.md")))
    files.extend(sorted((source_root / "schemas").glob("*.json")))
    return {path.relative_to(source_root): path.read_bytes() for path in files}


def differences(source_root: Path, target_root: Path) -> list[str]:
    expected = source_files(source_root)
    differences: list[str] = []
    for relative, expected_bytes in expected.items():
        target = target_root / relative
        if not target.is_file():
            differences.append(f"missing: {relative}")
        elif target.read_bytes() != expected_bytes:
            differences.append(f"different: {relative}")
    if target_root.exists():
        expected_paths = set(expected)
        for path in sorted(target_root.rglob("*")):
            if path.is_file() and path.relative_to(target_root) not in expected_paths:
                differences.append(f"unexpected (preserved): {path.relative_to(target_root)}")
    return differences


def mirror(source_root: Path, target_root: Path) -> None:
    for relative, content in source_files(source_root).items():
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or target.read_bytes() != content:
            target.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check for drift (the default)")
    parser.add_argument("--write", action="store_true", help="explicitly mirror source into portable package")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="portable package directory")
    args = parser.parse_args()

    if args.check and args.write:
        parser.error("--check and --write are mutually exclusive")
    if args.write:
        mirror(SOURCE_ROOT, args.target)
    drift = differences(SOURCE_ROOT, args.target)
    if drift:
        print("orchestration package drift:", *drift, sep="\n- ", file=sys.stderr)
        return 1
    print("orchestration package sync: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
