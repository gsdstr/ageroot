#!/usr/bin/env python3
"""Validate the canonical orchestration skill; optionally mirror an explicit target."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / 'skills/ageroot-orchestrate'


def source_files(source_root: Path) -> dict:
    return {p.relative_to(source_root): p.read_bytes() for p in sorted(source_root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo')}


def differences(source_root: Path, target_root: Path) -> list:
    expected = source_files(source_root)
    drift = []
    for relative, content in expected.items():
        target = target_root / relative
        if not target.is_file():
            drift.append(f'missing: {relative}')
        elif target.read_bytes() != content:
            drift.append(f'different: {relative}')
    for relative in source_files(target_root):
        if relative not in expected:
            drift.append(f'unexpected (preserved): {relative}')
    return drift


def mirror(source_root: Path, target_root: Path) -> None:
    for relative, content in source_files(source_root).items():
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or target.read_bytes() != content:
            target.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    parser.add_argument('--target', type=Path, help='optional explicit skill materialization directory')
    args = parser.parse_args()
    if args.write and args.target is None:
        parser.error('--write requires --target; canonical skill needs no implicit mirror')
    for required in ('SKILL.md', 'manifest.yaml', 'lifecycle-map.md', 'orca/adapter.py', 'orca/RUNBOOK.md'):
        if not (SOURCE_ROOT / required).is_file():
            parser.error(f'missing canonical skill file: {required}')
    if not (REPO_ROOT / 'skills/ageroot-roles/scripts/roles.py').is_file():
        parser.error('missing sibling role routing skill')
    subprocess.run([sys.executable, str(SOURCE_ROOT / 'scripts/validate.py'), '--package'], check=True)
    if args.target:
        if args.write:
            mirror(SOURCE_ROOT, args.target)
        drift = differences(SOURCE_ROOT, args.target)
        if drift:
            print('orchestration skill drift:', *drift, sep='\n- ', file=sys.stderr)
            return 1
    print('orchestration skill layout: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
