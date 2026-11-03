"""Collector module for discovering and rendering canonical payload files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ageroot_core.comparison import ManagedRegionParser
from ageroot_core.distribution.manifest import (
    DistributionComponent,
    MappingRule,
    get_default_components,
)

IGNORED_NAMES: Set[str] = {
    "__pycache__",
    ".DS_Store",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
}

IGNORED_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyo",
    ".swp",
}


def is_ignored_file(path: Path) -> bool:
    """Checks whether a path should be ignored during distribution collection."""
    for part in path.parts:
        if part in IGNORED_NAMES:
            return True
    if path.suffix in IGNORED_EXTENSIONS:
        return True
    return False


CollectedPayload = Tuple[Dict[str, str], List[Dict[str, str]]]


def collect_payload(
    repo_root: Path,
    selected_components: Optional[Sequence[str]] = None,
    component_catalog: Optional[Dict[str, DistributionComponent]] = None,
) -> CollectedPayload:
    """Discovers canonical files and renders them into (renders_map, managed_files_inventory).

    Args:
        repo_root: Path to the root of the Ageroot monorepo.
        selected_components: Sequence of component names to include. If None, default components are used.
        component_catalog: Catalog of components to use (defaults to get_default_components()).

    Returns:
        renders: dict mapping target relative paths (e.g. ".agents/protocols/permissions.md") to text content.
        managed_files: list of dicts {"path": str, "strategy": str} for state.yaml.
    """
    catalog = component_catalog or get_default_components()
    if selected_components is None:
        active_names = [name for name, comp in catalog.items() if comp.is_default]
    else:
        active_names = list(selected_components)

    renders: Dict[str, str] = {}
    managed_files: List[Dict[str, str]] = []
    seen_targets: Set[str] = set()

    for comp_name in active_names:
        if comp_name not in catalog:
            raise ValueError(f"Unknown distribution component: '{comp_name}'")
        component = catalog[comp_name]

        for rule in component.rules:
            src_full = (repo_root / rule.source_prefix).resolve()
            if not src_full.exists():
                raise FileNotFoundError(f"Canonical source missing for rule: {rule.source_prefix}")

            if src_full.is_file():
                if is_ignored_file(src_full):
                    continue
                target_rel = rule.target_prefix.replace("\\", "/")
                if target_rel not in seen_targets:
                    content = src_full.read_text(encoding="utf-8")
                    strategy = rule.strategy
                    if strategy != "managed-regions" and ManagedRegionParser.has_region_markers(content):
                        strategy = "managed-regions"
                    renders[target_rel] = content
                    managed_files.append({"path": target_rel, "strategy": strategy})
                    seen_targets.add(target_rel)
            elif src_full.is_dir():
                for root_dir, dirnames, filenames in os.walk(src_full):
                    # Filter out ignored directories in-place
                    dirnames[:] = [d for d in dirnames if d not in IGNORED_NAMES]

                    for filename in sorted(filenames):
                        file_path = Path(root_dir) / filename
                        if is_ignored_file(file_path):
                            continue

                        rel_within_src = file_path.relative_to(src_full).as_posix()
                        target_rel = f"{rule.target_prefix}/{rel_within_src}".replace("\\", "/")

                        if target_rel not in seen_targets:
                            content = file_path.read_text(encoding="utf-8")
                            strategy = rule.strategy
                            if strategy != "managed-regions" and ManagedRegionParser.has_region_markers(content):
                                strategy = "managed-regions"
                            renders[target_rel] = content
                            managed_files.append({"path": target_rel, "strategy": strategy})
                            seen_targets.add(target_rel)

    # Sort deterministically
    managed_files.sort(key=lambda item: item["path"])
    return renders, managed_files
