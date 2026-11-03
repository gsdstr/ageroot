#!/usr/bin/env python3
"""Ageroot Skill CLI: operational runner for check, plan, and apply."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Locate ageroot_core package in runtime or repo
SCRIPT_DIR = Path(__file__).resolve().parent
POSSIBLE_PACKAGE_ROOTS = [
    SCRIPT_DIR.parent.parent.parent / "packages",        # repo: skills/ageroot/scripts -> packages
    SCRIPT_DIR.parent.parent.parent.parent / "packages", # installed in repo: .agents/skills/ageroot/scripts -> packages
    Path.cwd() / "packages",
    SCRIPT_DIR.parent.parent.parent,                     # installed: .agents/skills/ageroot/scripts -> .agents
    Path.cwd() / ".agents",
]

for p in POSSIBLE_PACKAGE_ROOTS:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from ageroot_core.comparison import (
        AgerootUpdateEngine,
        ApplyOptions,
        ApplyOutcome,
        DryRunOptions,
        DryRunReport,
        format_summary,
    )
    from ageroot_core.distribution.collector import collect_payload
    from ageroot_core.distribution.service import DistributionService
except ImportError as err:
    print(f"Error: Unable to import ageroot_core: {err}", file=sys.stderr)
    print("Ensure packages/ or .agents/ageroot_core/ is accessible.", file=sys.stderr)
    sys.exit(1)


def cmd_check(service: DistributionService, target_dir: Path, components: Optional[List[str]]) -> int:
    """Check for drift against target directory."""
    clean, drift = service.check_drift(target_dir=target_dir, components=components)
    if not clean:
        print(f"Drift detected in {target_dir}:", file=sys.stderr)
        for item in drift:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"Check: PASS (no drift detected in {target_dir})")
    return 0


def cmd_plan(
    repo_root: Path,
    target_dir: Path,
    components: Optional[List[str]],
    allow_deletions: bool,
) -> int:
    """Execute safety-first dry run comparison."""
    renders, _ = collect_payload(repo_root, selected_components=components)
    engine = AgerootUpdateEngine(root_dir=target_dir)
    dry_run_opts = DryRunOptions(allow_deletions=allow_deletions)
    report = engine.dry_run(renders, options=dry_run_opts)
    print(format_summary(report))

    if not report.is_eligible:
        print(
            "Plan: NOT eligible for atomic apply (contains conflicts, blocked files, or unconfirmed deletions)",
            file=sys.stderr,
        )
        return 1
    print("Plan: ELIGIBLE for atomic apply")
    return 0


def cmd_apply(
    repo_root: Path,
    target_dir: Path,
    components: Optional[List[str]],
    allow_deletions: bool,
) -> int:
    """Execute atomic apply with transactional snapshot commit."""
    service = DistributionService(repo_root=repo_root)
    report, outcome = service.sync_local(
        target_dir=target_dir,
        components=components,
        allow_deletions=allow_deletions,
    )
    print(format_summary(report))
    if not outcome.success:
        print(f"Apply FAILED: {outcome.error}", file=sys.stderr)
        return 1
    print(
        f"Apply: SUCCESS ({len(outcome.applied_paths)} applied, {len(outcome.skipped_paths)} skipped)"
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ageroot",
        description="Ageroot operational tool: check drift, plan (dry-run), and apply updates.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    check_p = subparsers.add_parser("check", help="Check for drift against target directory")
    check_p.add_argument("--repo-root", type=Path, default=Path("."), help="Path to Ageroot repo root")
    check_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    check_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")

    # plan
    plan_p = subparsers.add_parser("plan", help="Run safety-first dry run comparison")
    plan_p.add_argument("--repo-root", type=Path, default=Path("."), help="Path to Ageroot repo root")
    plan_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    plan_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")
    plan_p.add_argument("--allow-deletions", action="store_true", help="Permit pending deletions")

    # apply
    apply_p = subparsers.add_parser("apply", help="Execute atomic update with snapshot commit")
    apply_p.add_argument("--repo-root", type=Path, default=Path("."), help="Path to Ageroot repo root")
    apply_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    apply_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")
    apply_p.add_argument("--allow-deletions", action="store_true", help="Permit pending deletions")

    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    target_dir = args.target.resolve()
    components = [c.strip() for c in args.components.split(",")] if args.components else None
    service = DistributionService(repo_root=repo_root)

    if args.command == "check":
        return cmd_check(service, target_dir, components)
    elif args.command == "plan":
        return cmd_plan(repo_root, target_dir, components, args.allow_deletions)
    elif args.command == "apply":
        return cmd_apply(repo_root, target_dir, components, args.allow_deletions)

    return 0


if __name__ == "__main__":
    sys.exit(main())
