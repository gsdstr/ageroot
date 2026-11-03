"""Ageroot distribution module."""

from ageroot_core.distribution.collector import collect_payload
from ageroot_core.distribution.manifest import (
    DistributionComponent,
    MappingRule,
    get_default_components,
)
from ageroot_core.distribution.service import DistributionService

__all__ = [
    "collect_payload",
    "DistributionComponent",
    "MappingRule",
    "get_default_components",
    "DistributionService",
]
