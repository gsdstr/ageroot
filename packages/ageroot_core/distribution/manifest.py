"""Declarative distribution manifest and component registry for Ageroot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MappingRule:
    """Mapping from a source directory or file to a destination in the payload."""
    source_prefix: str
    target_prefix: str
    strategy: str = "generated"
    pattern: str = "**/*"


@dataclass
class DistributionComponent:
    """A named, independently selectable distribution unit."""
    name: str
    description: str
    is_default: bool
    rules: List[MappingRule] = field(default_factory=list)


def get_default_components() -> Dict[str, DistributionComponent]:
    """Returns the canonical catalog of Ageroot distribution components."""
    return {
        "core": DistributionComponent(
            name="core",
            description="Core agent instructions, protocols, rules, and Update engine",
            is_default=True,
            rules=[
                MappingRule(
                    source_prefix="templates/core/AGENTS.md",
                    target_prefix="AGENTS.md",
                    strategy="managed-regions",
                ),
                MappingRule(
                    source_prefix="templates/core/.agents/AGENTS.md",
                    target_prefix=".agents/AGENTS.md",
                    strategy="managed-regions",
                ),
                MappingRule(
                    source_prefix="templates/core/.agents/PREFERENCES.md",
                    target_prefix=".agents/PREFERENCES.md",
                    strategy="generated",
                ),
                MappingRule(
                    source_prefix="templates/core/.agents/ageroot.config.yaml",
                    target_prefix=".agents/ageroot.config.yaml",
                    strategy="generated",
                ),
                MappingRule(
                    source_prefix="templates/core/.agents/rules",
                    target_prefix=".agents/rules",
                    strategy="generated",
                    pattern="**/*",
                ),
                MappingRule(
                    source_prefix="templates/core/.agents/protocols",
                    target_prefix=".agents/protocols",
                    strategy="generated",
                    pattern="**/*",
                ),
                MappingRule(
                    source_prefix="packages/ageroot_core",
                    target_prefix=".agents/ageroot_core",
                    strategy="generated",
                    pattern="**/*",
                ),
            ],
        ),
        "orchestration": DistributionComponent(
            name="orchestration",
            description="Neutral portable orchestration package specification and templates",
            is_default=True,
            rules=[
                MappingRule(
                    source_prefix="templates/orchestration/v1",
                    target_prefix=".agents/orchestration",
                    strategy="generated",
                    pattern="**/*",
                ),
            ],
        ),
        "orca_adapter": DistributionComponent(
            name="orca_adapter",
            description="Orca orchestration adapter overlay and runbook",
            is_default=True,
            rules=[
                MappingRule(
                    source_prefix="templates/orchestration/orca",
                    target_prefix=".agents/orchestration/orca",
                    strategy="generated",
                    pattern="**/*",
                ),
            ],
        ),
        "memory": DistributionComponent(
            name="memory",
            description="First-party memory-manager and memory-maintenance skills (opt-in)",
            is_default=False,
            rules=[
                MappingRule(
                    source_prefix="skills/memory-manager",
                    target_prefix=".agents/skills/memory-manager",
                    strategy="generated",
                    pattern="**/*",
                ),
                MappingRule(
                    source_prefix="skills/memory-maintenance",
                    target_prefix=".agents/skills/memory-maintenance",
                    strategy="generated",
                    pattern="**/*",
                ),
            ],
        ),
    }
