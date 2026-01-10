"""
Parameter Standardization Module for Neurop Block Forge V2.

This module provides tools for standardizing parameter names across blocks,
enabling consistent semantic composition and runtime execution.
"""

from neurop_forge.standardization.canonical_names import (
    CANONICAL_NAMES,
    CANONICAL_BY_TYPE,
    get_canonical_name,
    is_canonical,
)
from neurop_forge.standardization.parameter_mapper import (
    ParameterMapper,
    ParameterMapping,
)
from neurop_forge.standardization.interface_normalizer import (
    InterfaceNormalizer,
    NormalizationResult,
)

__all__ = [
    "CANONICAL_NAMES",
    "CANONICAL_BY_TYPE",
    "get_canonical_name",
    "is_canonical",
    "ParameterMapper",
    "ParameterMapping",
    "InterfaceNormalizer",
    "NormalizationResult",
]
