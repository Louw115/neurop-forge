"""Core modules for NeuropBlock identity, schema, and normalization."""

from neurop_forge.core.identity import IdentityAuthority
from neurop_forge.core.block_schema import NeuropBlock, BlockInterface, BlockConstraints, BlockMetadata
from neurop_forge.core.normalization import CodeNormalizer
from neurop_forge.core.block_tier import (
    BlockTier,
    TierClassification,
    TierRegistry,
    BlockTierClassifier,
    get_tier_registry,
    classify_blocks,
    print_tier_summary,
)
from neurop_forge.core.ai_metadata import (
    OperationType,
    CompositionRole,
    InputComplexity,
    AIMetadata,
    AIMetadataRegistry,
    generate_ai_metadata,
    enrich_blocks_with_ai_metadata,
    get_ai_metadata_registry,
)

__all__ = [
    "IdentityAuthority",
    "NeuropBlock",
    "BlockInterface",
    "BlockConstraints",
    "BlockMetadata",
    "CodeNormalizer",
    "BlockTier",
    "TierClassification",
    "TierRegistry",
    "BlockTierClassifier",
    "get_tier_registry",
    "classify_blocks",
    "print_tier_summary",
    "OperationType",
    "CompositionRole",
    "InputComplexity",
    "AIMetadata",
    "AIMetadataRegistry",
    "generate_ai_metadata",
    "enrich_blocks_with_ai_metadata",
    "get_ai_metadata_registry",
]
