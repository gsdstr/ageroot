"""CLI entry point for Ageroot distribution module."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from ageroot_core.comparison import format_summary
from ageroot_core.distribution.service import DistributionService


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m ageroot_core.distribution",
        description="Ageroot Distribution Module: whole-payload check, export, and local sync.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Check for drift between canonical payload and target directory",
    )
    group.add_argument(
        "--export",
        metavar="DIR",
        type=Path,
        help="Export reproducible distribution payload to DIR",
    )
    group.add_argument(
        "--sync-local",
        action="store_true",
        help="Sync canonical payload into target directory via Update engine",
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Path to Ageroot monorepo root (default: current directory)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("."),
        help="Target directory for check or sync (default: current directory)",
    )
    parser.add_argument(
        "--components",
        type=str,
        default=None,
        help="Comma-separated component list (e.g. 'core,orchestration,orca_adapter,memory')",
    )
    parser.add_argument(
        "--allow-deletions",
        action="store_true",
        help="Explicitly permit deletion of absent managed files during sync",
    )

    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    target_dir = args.target.resolve()
    components = [c.strip() for c in args.components.split(",")] if args.components else None

    service = DistributionService(repo_root=repo_root)

    if args.check:
        clean, drift = service.check_drift(target_dir=target_dir, components=components)
        if not clean:
            print(f"Drift detected in {target_dir}:", file=sys.stderr)
            for item in drift:
                print(f"  - {item}", file=sys.stderr)
            return 1
        print(f"Whole-payload check: PASS ({target_dir})")
        return 0

    elif args.export:
        out_dir = args.export.resolve()
        service.export_payload(output_dir=out_dir, components=components)
        print(f"Exported distribution payload to {out_dir}")
        return 0

    elif args.sync_local:
        report, outcome = service.sync_local(
            target_dir=target_dir,
            components=components,
            allow_deletions=args.allow_deletions,
        )
        print(format_summary(report))
        if not outcome.success:
            print(f"Sync failed: {outcome.error}", file=sys.stderr)
            return 1
        print(f"Local sync: SUCCESS ({len(outcome.applied_paths)} applied, {len(outcome.skipped_paths)} skipped)")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
