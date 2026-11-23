#!/usr/bin/env python3
"""Ageroot Skill CLI: operational runner for check, plan, apply, and snapshot-sync."""

from __future__ import annotations

import argparse
import os
import subprocess
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
    if (p / "ageroot_core" / "__init__.py").is_file():
        if str(p) in sys.path:
            sys.path.remove(str(p))
        sys.path.insert(0, str(p))
        break

try:
    from ageroot_core.comparison import (
        AgerootUpdateEngine,
        ApplyOptions,
        ApplyOutcome,
        DryRunOptions,
        DryRunReport,
        SimpleYamlHelper,
        SnapshotStore,
        format_summary,
    )
    from ageroot_core.distribution.collector import collect_payload
    from ageroot_core.distribution.service import DistributionService
except ImportError as err:
    print(f"Error: Unable to import ageroot_core: {err}", file=sys.stderr)
    print("Ensure packages/ or .agents/ageroot_core/ is accessible.", file=sys.stderr)
    sys.exit(1)


def is_valid_repo_root(p: Path) -> bool:
    """Checks if directory contains canonical Ageroot templates."""
    return (p / "templates" / "core").exists()


def resolve_repo_root(cli_arg: Optional[Path], target_dir: Path) -> Path:
    """Resolves the canonical Ageroot monorepo root across CLI, env, config, siblings, workspaces, and cache."""
    # 1. Explicit CLI argument (if not default or if valid)
    if cli_arg and cli_arg != Path("."):
        resolved = cli_arg.resolve()
        if is_valid_repo_root(resolved):
            return resolved

    # 2. Target directory (when running directly in monorepo root)
    if is_valid_repo_root(target_dir):
        return target_dir.resolve()

    # 3. Upward search from script location (catches development checkouts)
    for parent in [SCRIPT_DIR] + list(SCRIPT_DIR.parents):
        if is_valid_repo_root(parent):
            return parent.resolve()

    # 4. Sibling directories relative to target directory and script directory
    sibling_candidates = [
        target_dir.parent / "ageroot",
        target_dir.parent.parent / "ageroot",
        SCRIPT_DIR.parent.parent.parent.parent / "ageroot",
        SCRIPT_DIR.parent.parent.parent.parent.parent / "ageroot",
    ]
    for sib in sibling_candidates:
        if sib.exists() and is_valid_repo_root(sib):
            return sib.resolve()

    # 5. Environment variable AGEROOT_REPO_ROOT
    env_root = os.environ.get("AGEROOT_REPO_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser().resolve()
        if is_valid_repo_root(env_path):
            return env_path

    # 6. Config file .agents/ageroot.config.yaml or state file
    for meta_file in (target_dir / ".agents" / "ageroot.config.yaml", target_dir / ".agents" / "ageroot.state.yaml"):
        if meta_file.exists():
            try:
                data = SimpleYamlHelper.parse(meta_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    tmpl = data.get("template", {})
                    if isinstance(tmpl, dict) and "repo_root" in tmpl:
                        cfg_path = Path(tmpl["repo_root"]).expanduser().resolve()
                        if is_valid_repo_root(cfg_path):
                            return cfg_path
            except Exception:
                pass

    # 7. Global user config (~/.config/ageroot/config.yaml or roles.yaml)
    global_cfg_dirs = [
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ageroot",
        Path.home() / ".config" / "ageroot",
    ]
    for gcd in global_cfg_dirs:
        for fname in ("config.yaml", "roles.yaml"):
            gfile = gcd / fname
            if gfile.exists():
                try:
                    data = SimpleYamlHelper.parse(gfile.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        tmpl = data.get("template", {})
                        root_val = tmpl.get("repo_root") if isinstance(tmpl, dict) else data.get("template_repo_root")
                        if root_val:
                            g_path = Path(root_val).expanduser().resolve()
                            if is_valid_repo_root(g_path):
                                return g_path
                except Exception:
                    pass

    # 8. Standard developer workspace paths
    home = Path.home()
    workspace_candidates = [
        home / "hub" / "0_efforts" / "ageroot",
        home / "projects" / "ageroot",
        home / "code" / "ageroot",
        home / "src" / "ageroot",
        home / "dev" / "ageroot",
        home / "workspace" / "ageroot",
        home / "work" / "ageroot",
        home / "repos" / "ageroot",
        home / ".local" / "share" / "ageroot",
    ]
    for cand in workspace_candidates:
        if cand.exists() and is_valid_repo_root(cand):
            return cand.resolve()

    # 9. APM cache search across platform locations
    apm_cache_dirs = [
        home / "Library" / "Caches" / "apm" / "git" / "checkouts_v1",
        home / ".cache" / "apm" / "git" / "checkouts_v1",
        Path(os.environ.get("XDG_CACHE_HOME", home / ".cache")) / "apm" / "git" / "checkouts_v1",
    ]
    for cache_root in apm_cache_dirs:
        if cache_root.exists():
            for core_dir in cache_root.rglob("templates/core"):
                candidate = core_dir.parent.parent
                if is_valid_repo_root(candidate):
                    return candidate.resolve()

    # 10. System cache directories (XDG_CACHE_HOME, macOS ~/Library/Caches, ~/.cache)
    cache_dirs = [
        home / ".cache" / "ageroot" / "templates",
        home / "Library" / "Caches" / "ageroot" / "templates",
        Path(os.environ.get("XDG_CACHE_HOME", home / ".cache")) / "ageroot" / "templates",
        Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")) / "ageroot" / "templates",
    ]
    for cdir in cache_dirs:
        if is_valid_repo_root(cdir):
            if (cdir / ".git").is_dir() and not cdir.is_symlink():
                try:
                    subprocess.run(
                        ["git", "-C", str(cdir), "pull", "--ff-only"],
                        capture_output=True,
                        timeout=5,
                    )
                except Exception:
                    pass
            return cdir.resolve()

    # 11. Automatic shallow clone if git and source are available
    primary_cache = Path(os.environ.get("XDG_CACHE_HOME", home / ".cache")) / "ageroot" / "templates"
    source_url = "https://github.com/gsdstr/ageroot.git"
    state_file = target_dir / ".agents" / "ageroot.state.yaml"
    if state_file.exists():
        try:
            state = SimpleYamlHelper.parse(state_file.read_text(encoding="utf-8"))
            if isinstance(state, dict):
                tmpl_state = state.get("template", {})
                if isinstance(tmpl_state, dict):
                    src = tmpl_state.get("source")
                    if src and (src.startswith("http") or src.startswith("git@")):
                        source_url = src
        except Exception:
            pass

    try:
        primary_cache.parent.mkdir(parents=True, exist_ok=True)
        print(f"Fetching canonical Ageroot templates from {source_url}...", file=sys.stderr)
        res = subprocess.run(
            ["git", "clone", "--depth", "1", source_url, str(primary_cache)],
            capture_output=True,
            text=True,
            timeout=45,
        )
        if res.returncode == 0 and is_valid_repo_root(primary_cache):
            return primary_cache.resolve()
    except Exception as err:
        print(f"Warning: automatic template clone failed: {err}", file=sys.stderr)

    # 12. Fallback failure with actionable instructions
    print(
        "Error: Cannot locate Ageroot templates (templates/core/).\n"
        "In a consuming project, please supply the template repository root via:\n"
        "  1. CLI option:           --repo-root /path/to/ageroot\n"
        "  2. Environment variable: AGEROOT_REPO_ROOT=/path/to/ageroot\n"
        "  3. Configuration:        template.repo_root in .agents/ageroot.config.yaml\n"
        "  4. Sibling clone:        Clone ageroot beside your project repository\n"
        "  5. Global config:        template_repo_root in ~/.config/ageroot/config.yaml",
        file=sys.stderr,
    )
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
    unverified_override: bool = False,
) -> int:
    """Execute safety-first dry run comparison."""
    renders, _ = collect_payload(repo_root, selected_components=components)
    engine = AgerootUpdateEngine(root_dir=target_dir)
    dry_run_opts = DryRunOptions(
        allow_deletions=allow_deletions,
        one_time_unverified_override=unverified_override,
    )
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
    unverified_override: bool = False,
) -> int:
    """Execute atomic update with transactional snapshot commit."""
    service = DistributionService(repo_root=repo_root)
    report, outcome = service.sync_local(
        target_dir=target_dir,
        components=components,
        allow_deletions=allow_deletions,
        one_time_unverified_override=unverified_override,
    )
    print(format_summary(report))
    if not outcome.success:
        print(f"Apply FAILED: {outcome.error}", file=sys.stderr)
        return 1
    print(
        f"Apply: SUCCESS ({len(outcome.applied_paths)} applied, {len(outcome.skipped_paths)} skipped)"
    )
    return 0


def cmd_snapshot_sync(target_dir: Path) -> int:
    """Reconstruct missing snapshots from workspace files matching state SHA-256."""
    state_file = target_dir / ".agents" / "ageroot.state.yaml"
    if not state_file.exists():
        print(f"Error: state file not found at {state_file}", file=sys.stderr)
        return 1

    state = SimpleYamlHelper.parse(state_file.read_text(encoding="utf-8"))
    managed = state.get("managed_files", []) if isinstance(state, dict) else []
    store = SnapshotStore(root_dir=target_dir)
    reconstructed, skipped = store.sync_from_workspace(managed)

    print(f"Snapshot sync: {len(reconstructed)} reconstructed, {len(skipped)} skipped/mismatched.")
    for p in reconstructed:
        print(f"  + reconstructed: {p}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ageroot",
        description="Ageroot operational tool: check drift, plan (dry-run), apply updates, and sync snapshots.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    check_p = subparsers.add_parser("check", help="Check for drift against target directory")
    check_p.add_argument("--repo-root", type=Path, default=None, help="Path to Ageroot repo root")
    check_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    check_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")

    # plan
    plan_p = subparsers.add_parser("plan", help="Run safety-first dry run comparison")
    plan_p.add_argument("--repo-root", type=Path, default=None, help="Path to Ageroot repo root")
    plan_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    plan_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")
    plan_p.add_argument("--allow-deletions", action="store_true", help="Permit pending deletions")
    plan_p.add_argument(
        "--unverified-override",
        action="store_true",
        help="Permit one-time unverified override for missing or corrupt baseline snapshots",
    )

    # apply
    apply_p = subparsers.add_parser("apply", help="Execute atomic update with snapshot commit")
    apply_p.add_argument("--repo-root", type=Path, default=None, help="Path to Ageroot repo root")
    apply_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")
    apply_p.add_argument("--components", type=str, default=None, help="Comma-separated component list")
    apply_p.add_argument("--allow-deletions", action="store_true", help="Permit pending deletions")
    apply_p.add_argument(
        "--unverified-override",
        action="store_true",
        help="Permit one-time unverified override for missing or corrupt baseline snapshots",
    )

    # snapshot-sync
    sync_p = subparsers.add_parser(
        "snapshot-sync",
        aliases=["sync-snapshots"],
        help="Reconstruct missing snapshots from workspace files matching state SHA-256",
    )
    sync_p.add_argument("--target", type=Path, default=Path("."), help="Target directory (default: .)")

    args = parser.parse_args(argv)
    target_dir = args.target.resolve()

    if args.command in ("snapshot-sync", "sync-snapshots"):
        return cmd_snapshot_sync(target_dir)

    repo_root = resolve_repo_root(args.repo_root, target_dir)
    components = [c.strip() for c in args.components.split(",")] if args.components else None
    service = DistributionService(repo_root=repo_root)

    if args.command == "check":
        return cmd_check(service, target_dir, components)
    elif args.command == "plan":
        return cmd_plan(
            repo_root,
            target_dir,
            components,
            args.allow_deletions,
            args.unverified_override,
        )
    elif args.command == "apply":
        return cmd_apply(
            repo_root,
            target_dir,
            components,
            args.allow_deletions,
            args.unverified_override,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
