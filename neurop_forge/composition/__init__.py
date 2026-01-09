"""Composition modules for block compatibility and graph rules."""

from neurop_forge.composition.compatibility import CompatibilityChecker, CompatibilityResult
from neurop_forge.composition.graph_rules import GraphValidator, ValidationResult

__all__ = [
    "CompatibilityChecker",
    "CompatibilityResult",
    "GraphValidator",
    "ValidationResult",
]
