"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com

Semantic Intent Layer - Makes composition work.
"""

from neurop_forge.semantic.intent_schema import (
    SemanticDomain,
    SemanticOperation,
    SemanticType,
    SemanticIntent,
    can_chain,
    are_semantic_types_compatible,
    get_operation_order,
    DOMAIN_CHAIN_RULES,
    OPERATION_ORDER,
    SEMANTIC_TYPE_COMPATIBILITY,
)
