"""Distribution service for whole-payload drift checking, export, and local sync."""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ageroot_core.comparison import (
    AgerootUpdateEngine,
    ApplyOptions,
    ApplyOutcome,
    DeterministicNormalizer,
    DryRunOptions,
    DryRunReport,
    ManagedRegionParser,
    ResultClass,
    SimpleYamlHelper,
    format_summary,
)
from ageroot_core.distribution.collector import collect_payload, is_ignored_file


def get_git_commit(repo_root: Path) -> str:
    """Gets short git commit hash or 'unknown'."""
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


class DistributionService:
    """Coordinates whole-payload export, drift checking, and local sync."""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root).resolve()

    def check_drift(
        self,
        target_dir: Path,
        components: Optional[Sequence[str]] = None,
    ) -> Tuple[bool, List[str]]:
        """Checks for drift between canonical payload and target directory.

        Returns:
            (is_clean, drift_messages)
        """
        target = Path(target_dir).resolve()
        renders, _ = collect_payload(self.repo_root, selected_components=components)

        drift: List[str] = []
        expected_paths: Set[str] = set()

        for rel_path, expected_content in renders.items():
            expected_paths.add(rel_path)
            dest_file = target / rel_path

            if not dest_file.exists():
                drift.append(f"missing: {rel_path}")
            elif not dest_file.is_file():
                drift.append(f"not-a-file: {rel_path}")
            else:
                try:
                    actual_content = dest_file.read_text(encoding="utf-8")
                    norm_actual = DeterministicNormalizer.normalize_text(actual_content)
                    norm_expected = DeterministicNormalizer.normalize_text(expected_content)
                    if norm_actual != norm_expected:
                        if ManagedRegionParser.has_region_markers(expected_content):
                            merge_res = ManagedRegionParser.merge(actual_content, expected_content)
                            if merge_res.result_class in (ResultClass.UNCHANGED, ResultClass.REGION_MERGE):
                                continue
                        drift.append(f"modified: {rel_path}")
                except Exception as ex:
                    drift.append(f"read-error: {rel_path} ({ex})")

        # Check for unexpected files in managed prefixes
        managed_prefixes = [
            ".agents/orchestration",
            ".agents/ageroot_core",
            ".agents/protocols",
            ".agents/rules",
        ]
        if components and "memory" in components:
            managed_prefixes.append(".agents/skills/memory-manager")
            managed_prefixes.append(".agents/skills/memory-maintenance")

        for prefix in managed_prefixes:
            prefix_dir = target / prefix
            if prefix_dir.exists() and prefix_dir.is_dir():
                for root, dirnames, filenames in os.walk(prefix_dir):
                    dirnames[:] = [d for d in dirnames if not is_ignored_file(Path(d))]
                    for f in filenames:
                        file_path = Path(root) / f
                        if is_ignored_file(file_path):
                            continue
                        rel_path = file_path.relative_to(target).as_posix()
                        if rel_path not in expected_paths:
                            drift.append(f"unexpected: {rel_path}")

        return (len(drift) == 0, drift)

    def export_payload(
        self,
        output_dir: Path,
        components: Optional[Sequence[str]] = None,
        commit: Optional[str] = None,
    ) -> Path:
        """Exports a clean, reproducible distribution payload to output_dir with baseline snapshots."""
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)

        renders, managed_files_templates = collect_payload(self.repo_root, selected_components=components)
        commit_hash = commit or get_git_commit(self.repo_root)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        strategy_map = {item["path"]: item["strategy"] for item in managed_files_templates}
        managed_files: List[dict] = []
        snapshots_dir = out / ".agents" / "snapshots"

        # Write each rendered file and its initial baseline snapshot
        for rel_path, content in renders.items():
            dest_file = out / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(content, encoding="utf-8")

            # Normalise content for snapshot as Update engine does
            from ageroot_core.comparison import DeterministicNormalizer, SnapshotStore
            norm_content = DeterministicNormalizer.normalize_text(content)
            sha256 = SnapshotStore.compute_sha256(norm_content)

            snap_file = snapshots_dir / rel_path
            snap_file.parent.mkdir(parents=True, exist_ok=True)
            snap_file.write_text(norm_content, encoding="utf-8")

            strategy = strategy_map.get(rel_path, "generated")
            managed_files.append({
                "path": rel_path,
                "strategy": strategy,
                "snapshot": f".agents/snapshots/{rel_path}",
                "sha256": sha256,
            })

        # Generate and write state file with expanded concrete files
        state_data = {
            "schema": 1,
            "template": {
                "name": "ageroot",
                "version": "0.1.0",
                "source": "canonical",
                "commit": commit_hash,
            },
            "installed_at": now_iso,
            "rendered_at": now_iso,
            "managed_files": managed_files,
        }
        state_file = out / ".agents" / "ageroot.state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(SimpleYamlHelper.dump(state_data), encoding="utf-8")

        return out

    def sync_local(
        self,
        target_dir: Path,
        components: Optional[Sequence[str]] = None,
        allow_deletions: bool = False,
    ) -> Tuple[DryRunReport, ApplyOutcome]:
        """Runs the Update engine dry-run and atomic apply against target_dir."""
        target = Path(target_dir).resolve()
        renders, _ = collect_payload(self.repo_root, selected_components=components)

        engine = AgerootUpdateEngine(root_dir=target)
        dry_run_opts = DryRunOptions(allow_deletions=allow_deletions)
        report = engine.dry_run(renders, options=dry_run_opts)

        apply_opts = ApplyOptions(allow_deletions=allow_deletions)
        outcome = engine.apply(report, options=apply_opts)
        return report, outcome
