"""
Copyright 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

AI Composition Metadata

Enhanced metadata for AI-assisted block selection and composition.
This module provides rich semantic context that helps AI:
1. Select the right blocks for an intent
2. Order blocks correctly in a composition
3. Predict input/output compatibility
4. Avoid composition anti-patterns
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import json
from pathlib import Path


class OperationType(Enum):
    """High-level operation categories for block composition ordering."""
    VALIDATE = "validate"
    CHECK = "check"
    PARSE = "parse"
    TRANSFORM = "transform"
    FORMAT = "format"
    CALCULATE = "calculate"
    AGGREGATE = "aggregate"
    FILTER = "filter"
    SORT = "sort"
    SEARCH = "search"
    COMPARE = "compare"
    CONVERT = "convert"
    ENCODE = "encode"
    DECODE = "decode"
    GENERATE = "generate"
    EXTRACT = "extract"
    MERGE = "merge"
    SPLIT = "split"


class CompositionRole(Enum):
    """Role a block typically plays in a composition graph."""
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    TERMINAL = "terminal"
    STANDALONE = "standalone"
    BRANCHING = "branching"
    JOINING = "joining"


class InputComplexity(Enum):
    """How complex the input requirements are."""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class CompositionHints:
    """Hints for AI to compose blocks correctly."""
    preferred_predecessors: List[str] = field(default_factory=list)
    preferred_successors: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    synergies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "preferred_predecessors": self.preferred_predecessors,
            "preferred_successors": self.preferred_successors,
            "anti_patterns": self.anti_patterns,
            "synergies": self.synergies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositionHints":
        return cls(
            preferred_predecessors=data.get("preferred_predecessors", []),
            preferred_successors=data.get("preferred_successors", []),
            anti_patterns=data.get("anti_patterns", []),
            synergies=data.get("synergies", []),
        )


@dataclass
class AIMetadata:
    """
    Enhanced metadata for AI-assisted block composition.
    
    This metadata helps AI:
    - Select appropriate blocks based on semantic domain
    - Order blocks correctly (validation before transformation)
    - Predict compatibility between blocks
    - Avoid common composition mistakes
    """
    block_id: str
    block_name: str
    semantic_domain: str
    operation_type: OperationType
    composition_role: CompositionRole
    input_complexity: InputComplexity
    semantic_tags: List[str]
    example_inputs: Dict[str, Any] = field(default_factory=dict)
    example_outputs: Dict[str, Any] = field(default_factory=dict)
    composition_hints: CompositionHints = field(default_factory=CompositionHints)
    natural_language_description: str = ""
    use_cases: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "block_name": self.block_name,
            "semantic_domain": self.semantic_domain,
            "operation_type": self.operation_type.value,
            "composition_role": self.composition_role.value,
            "input_complexity": self.input_complexity.value,
            "semantic_tags": self.semantic_tags,
            "example_inputs": self.example_inputs,
            "example_outputs": self.example_outputs,
            "composition_hints": self.composition_hints.to_dict(),
            "natural_language_description": self.natural_language_description,
            "use_cases": self.use_cases,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIMetadata":
        return cls(
            block_id=data["block_id"],
            block_name=data["block_name"],
            semantic_domain=data["semantic_domain"],
            operation_type=OperationType(data["operation_type"]),
            composition_role=CompositionRole(data["composition_role"]),
            input_complexity=InputComplexity(data["input_complexity"]),
            semantic_tags=data.get("semantic_tags", []),
            example_inputs=data.get("example_inputs", {}),
            example_outputs=data.get("example_outputs", {}),
            composition_hints=CompositionHints.from_dict(data.get("composition_hints", {})),
            natural_language_description=data.get("natural_language_description", ""),
            use_cases=data.get("use_cases", []),
        )


class AIMetadataRegistry:
    """Registry of AI metadata for all blocks."""
    
    def __init__(self):
        self._metadata: Dict[str, AIMetadata] = {}
        self._path = Path(".neurop_verified/ai_metadata.json")
    
    def add(self, metadata: AIMetadata) -> None:
        """Add metadata for a block."""
        self._metadata[metadata.block_id] = metadata
    
    def get(self, block_id: str) -> Optional[AIMetadata]:
        """Get metadata for a block."""
        return self._metadata.get(block_id)
    
    def get_by_domain(self, domain: str) -> List[AIMetadata]:
        """Get all blocks in a semantic domain."""
        return [m for m in self._metadata.values() if m.semantic_domain == domain]
    
    def get_by_operation(self, op_type: OperationType) -> List[AIMetadata]:
        """Get all blocks with a specific operation type."""
        return [m for m in self._metadata.values() if m.operation_type == op_type]
    
    def get_by_tag(self, tag: str) -> List[AIMetadata]:
        """Get all blocks with a specific semantic tag."""
        return [m for m in self._metadata.values() if tag in m.semantic_tags]
    
    def get_entry_blocks(self) -> List[AIMetadata]:
        """Get blocks suitable as entry points."""
        return [m for m in self._metadata.values() 
                if m.composition_role in [CompositionRole.ENTRY, CompositionRole.STANDALONE]]
    
    def get_terminal_blocks(self) -> List[AIMetadata]:
        """Get blocks suitable as terminal points."""
        return [m for m in self._metadata.values() 
                if m.composition_role in [CompositionRole.TERMINAL, CompositionRole.STANDALONE]]
    
    def save(self) -> None:
        """Save registry to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.to_dict() for k, v in self._metadata.items()}
        self._path.write_text(json.dumps(data, indent=2))
    
    def load(self) -> None:
        """Load registry from disk."""
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for block_id, m in data.items():
                self._metadata[block_id] = AIMetadata.from_dict(m)
        except Exception:
            pass
    
    def count(self) -> int:
        """Get total number of blocks with AI metadata."""
        return len(self._metadata)
    
    def summary(self) -> Dict[str, int]:
        """Get summary by domain and operation type."""
        domains: Dict[str, int] = {}
        operations: Dict[str, int] = {}
        
        for m in self._metadata.values():
            domains[m.semantic_domain] = domains.get(m.semantic_domain, 0) + 1
            operations[m.operation_type.value] = operations.get(m.operation_type.value, 0) + 1
        
        return {
            "total": len(self._metadata),
            "by_domain": domains,
            "by_operation": operations,
        }


DOMAIN_OPERATION_MAP = {
    "string": [OperationType.TRANSFORM, OperationType.FORMAT, OperationType.PARSE],
    "validation": [OperationType.VALIDATE, OperationType.CHECK],
    "collection": [OperationType.FILTER, OperationType.SORT, OperationType.AGGREGATE],
    "filtering": [OperationType.FILTER, OperationType.SEARCH],
    "calculation": [OperationType.CALCULATE, OperationType.AGGREGATE],
    "transformation": [OperationType.TRANSFORM, OperationType.CONVERT],
    "io": [OperationType.PARSE, OperationType.FORMAT],
    "utility": [OperationType.TRANSFORM],
    "aggregation": [OperationType.AGGREGATE, OperationType.MERGE],
    "comparison": [OperationType.COMPARE, OperationType.CHECK],
    "formatting": [OperationType.FORMAT],
    "encoding": [OperationType.ENCODE, OperationType.DECODE],
    "parsing": [OperationType.PARSE, OperationType.EXTRACT],
}

NAME_OPERATION_PATTERNS = {
    "is_": OperationType.CHECK,
    "has_": OperationType.CHECK,
    "validate_": OperationType.VALIDATE,
    "check_": OperationType.CHECK,
    "parse_": OperationType.PARSE,
    "format_": OperationType.FORMAT,
    "to_": OperationType.CONVERT,
    "from_": OperationType.PARSE,
    "encode_": OperationType.ENCODE,
    "decode_": OperationType.DECODE,
    "extract_": OperationType.EXTRACT,
    "merge_": OperationType.MERGE,
    "split_": OperationType.SPLIT,
    "filter_": OperationType.FILTER,
    "sort_": OperationType.SORT,
    "aggregate_": OperationType.AGGREGATE,
    "calculate_": OperationType.CALCULATE,
    "compute_": OperationType.CALCULATE,
    "generate_": OperationType.GENERATE,
    "search_": OperationType.SEARCH,
    "find_": OperationType.SEARCH,
    "compare_": OperationType.COMPARE,
}


def infer_operation_type(block_name: str, domain: str) -> OperationType:
    """Infer operation type from block name and domain."""
    name_lower = block_name.lower()
    
    for prefix, op_type in NAME_OPERATION_PATTERNS.items():
        if name_lower.startswith(prefix):
            return op_type
    
    domain_ops = DOMAIN_OPERATION_MAP.get(domain, [OperationType.TRANSFORM])
    return domain_ops[0] if domain_ops else OperationType.TRANSFORM


def infer_composition_role(operation_type: OperationType, input_count: int, output_count: int) -> CompositionRole:
    """Infer composition role from operation type and interface."""
    if operation_type in [OperationType.VALIDATE, OperationType.CHECK]:
        return CompositionRole.ENTRY
    
    if operation_type in [OperationType.FORMAT]:
        return CompositionRole.TERMINAL
    
    if input_count == 0:
        return CompositionRole.ENTRY
    
    if input_count > 2:
        return CompositionRole.JOINING
    
    return CompositionRole.INTERMEDIATE


def infer_input_complexity(inputs: List) -> InputComplexity:
    """Infer input complexity from input parameters."""
    count = len(inputs)
    
    if count == 0:
        return InputComplexity.TRIVIAL
    elif count == 1:
        return InputComplexity.SIMPLE
    elif count <= 3:
        return InputComplexity.MODERATE
    else:
        return InputComplexity.COMPLEX


def generate_ai_metadata(block, domain: str) -> AIMetadata:
    """Generate AI metadata for a block automatically."""
    from neurop_forge.core.block_schema import NeuropBlock
    
    block_id = block.get_identity_hash() if hasattr(block, 'get_identity_hash') else str(id(block))
    block_name = block.metadata.name if hasattr(block.metadata, 'name') else "unknown"
    
    operation_type = infer_operation_type(block_name, domain)
    input_count = len(block.interface.inputs)
    output_count = len(block.interface.outputs)
    composition_role = infer_composition_role(operation_type, input_count, output_count)
    input_complexity = infer_input_complexity(list(block.interface.inputs))
    
    tags = list(block.metadata.tags) if hasattr(block.metadata, 'tags') else []
    tags.append(domain)
    tags.append(operation_type.value)
    
    description = block.metadata.description if hasattr(block.metadata, 'description') else ""
    
    return AIMetadata(
        block_id=block_id,
        block_name=block_name,
        semantic_domain=domain,
        operation_type=operation_type,
        composition_role=composition_role,
        input_complexity=input_complexity,
        semantic_tags=list(set(tags)),
        natural_language_description=description,
    )


def enrich_blocks_with_ai_metadata(blocks: List, domain_lookup: Dict[str, str]) -> AIMetadataRegistry:
    """Enrich all blocks with AI metadata."""
    registry = AIMetadataRegistry()
    registry.load()
    
    for block in blocks:
        block_id = block.get_identity_hash() if hasattr(block, 'get_identity_hash') else str(id(block))
        domain = domain_lookup.get(block_id, "utility")
        
        metadata = generate_ai_metadata(block, domain)
        registry.add(metadata)
    
    registry.save()
    return registry


_ai_registry: Optional[AIMetadataRegistry] = None


def get_ai_metadata_registry() -> AIMetadataRegistry:
    """Get the global AI metadata registry."""
    global _ai_registry
    if _ai_registry is None:
        _ai_registry = AIMetadataRegistry()
        _ai_registry.load()
    return _ai_registry
