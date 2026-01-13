"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Semantic Composer - Composes block graphs using semantic intent matching.

This is the CORE component that makes Neurop work properly.
Instead of keyword matching, it uses:
1. Semantic domain matching
2. Type flow validation
3. Operation ordering
4. Pre/postcondition satisfaction
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum

from neurop_forge.semantic.intent_schema import (
    SemanticIntent,
    SemanticDomain,
    SemanticOperation,
    SemanticType,
    can_chain,
    are_semantic_types_compatible,
    get_operation_order,
)


@dataclass
class SemanticIndexEntry:
    """Index entry with full semantic information."""
    block_identity: str
    name: str
    description: str
    category: str
    semantic_intent: SemanticIntent
    input_data_types: Tuple[str, ...]
    output_data_types: Tuple[str, ...]
    trust_score: float
    is_pure: bool
    is_deterministic: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "semantic_intent": self.semantic_intent.to_dict(),
            "input_data_types": list(self.input_data_types),
            "output_data_types": list(self.output_data_types),
            "trust_score": self.trust_score,
            "is_pure": self.is_pure,
            "is_deterministic": self.is_deterministic,
        }


@dataclass
class CompositionNode:
    """A node in a semantic composition graph."""
    block_identity: str
    block_name: str
    semantic_intent: SemanticIntent
    position: int
    why_selected: str
    input_sources: Tuple[str, ...]
    output_targets: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "block_name": self.block_name,
            "semantic_intent": self.semantic_intent.to_dict(),
            "position": self.position,
            "why_selected": self.why_selected,
            "input_sources": list(self.input_sources),
            "output_targets": list(self.output_targets),
        }


@dataclass
class SemanticGraph:
    """A semantically validated composition graph."""
    query: str
    intent_analysis: Dict[str, Any]
    nodes: Tuple[CompositionNode, ...]
    edges: Tuple[Tuple[str, str, str], ...]
    is_valid: bool
    validation_details: Tuple[str, ...]
    total_trust_score: float
    composition_confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "intent_analysis": self.intent_analysis,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [{"from": e[0], "to": e[1], "type": e[2]} for e in self.edges],
            "is_valid": self.is_valid,
            "validation_details": list(self.validation_details),
            "total_trust_score": self.total_trust_score,
            "composition_confidence": self.composition_confidence,
        }


class QueryIntentParser:
    """Parses natural language queries into semantic requirements."""
    
    INTENT_PATTERNS = {
        ("validate", "and", "format"): [SemanticDomain.VALIDATION, SemanticDomain.FORMATTING],
        ("check", "and", "convert"): [SemanticDomain.VALIDATION, SemanticDomain.TRANSFORMATION],
        ("parse", "and", "validate"): [SemanticDomain.PARSING, SemanticDomain.VALIDATION],
        ("sanitize", "and", "format"): [SemanticDomain.SECURITY, SemanticDomain.FORMATTING],
        ("calculate", "and", "format"): [SemanticDomain.CALCULATION, SemanticDomain.FORMATTING],
        ("search", "and", "filter"): [SemanticDomain.SEARCHING, SemanticDomain.FILTERING],
        ("transform", "and", "validate"): [SemanticDomain.TRANSFORMATION, SemanticDomain.VALIDATION],
    }
    
    SINGLE_DOMAIN_KEYWORDS = {
        "validate": SemanticDomain.VALIDATION,
        "check": SemanticDomain.VALIDATION,
        "verify": SemanticDomain.VALIDATION,
        "format": SemanticDomain.FORMATTING,
        "display": SemanticDomain.FORMATTING,
        "transform": SemanticDomain.TRANSFORMATION,
        "convert": SemanticDomain.TRANSFORMATION,
        "parse": SemanticDomain.PARSING,
        "extract": SemanticDomain.PARSING,
        "sanitize": SemanticDomain.SECURITY,
        "secure": SemanticDomain.SECURITY,
        "escape": SemanticDomain.SECURITY,
        "calculate": SemanticDomain.CALCULATION,
        "compute": SemanticDomain.CALCULATION,
        "add": SemanticDomain.CALCULATION,
        "addition": SemanticDomain.CALCULATION,
        "subtract": SemanticDomain.CALCULATION,
        "multiply": SemanticDomain.CALCULATION,
        "divide": SemanticDomain.CALCULATION,
        "sum": SemanticDomain.CALCULATION,
        "arithmetic": SemanticDomain.CALCULATION,
        "math": SemanticDomain.CALCULATION,
        "numbers": SemanticDomain.NUMERIC,
        "compare": SemanticDomain.COMPARISON,
        "filter": SemanticDomain.FILTERING,
        "search": SemanticDomain.SEARCHING,
        "find": SemanticDomain.SEARCHING,
        "sort": SemanticDomain.SORTING,
        "order": SemanticDomain.SORTING,
        "encode": SemanticDomain.ENCODING,
        "hash": SemanticDomain.HASHING,
        "string": SemanticDomain.STRING,
        "text": SemanticDomain.STRING,
        "number": SemanticDomain.NUMERIC,
        "date": SemanticDomain.DATETIME,
        "time": SemanticDomain.DATETIME,
    }
    
    SEMANTIC_TYPE_KEYWORDS = {
        "email": SemanticType.EMAIL,
        "url": SemanticType.URL,
        "phone": SemanticType.PHONE,
        "password": SemanticType.PASSWORD,
        "user": SemanticType.USER_DATA,
        "input": SemanticType.RAW_INPUT,
        "text": SemanticType.TEXT,
        "string": SemanticType.TEXT,
        "date": SemanticType.DATE,
        "time": SemanticType.TIME,
        "number": SemanticType.NUMERIC_VALUE,
        "currency": SemanticType.CURRENCY,
        "money": SemanticType.CURRENCY,
        "address": SemanticType.ADDRESS,
        "name": SemanticType.NAME,
        "json": SemanticType.JSON,
        "html": SemanticType.HTML,
        "token": SemanticType.TOKEN,
        "id": SemanticType.ID,
        "path": SemanticType.PATH,
        "color": SemanticType.COLOR,
    }

    def parse(self, query: str) -> Dict[str, Any]:
        """Parse query into semantic requirements."""
        query_lower = query.lower()
        words = query_lower.split()
        
        required_domains = self._extract_domains(query_lower, words)
        required_types = self._extract_semantic_types(words)
        required_operations = self._extract_operations(words)
        
        return {
            "original_query": query,
            "required_domains": required_domains,
            "required_semantic_types": required_types,
            "required_operations": required_operations,
            "is_multi_step": len(required_domains) > 1,
            "flow_direction": self._determine_flow(required_domains),
        }

    def _extract_domains(self, query: str, words: List[str]) -> List[SemanticDomain]:
        """Extract required domains from query."""
        for pattern, domains in self.INTENT_PATTERNS.items():
            if all(kw in query for kw in pattern):
                return domains
        
        domains: List[SemanticDomain] = []
        seen = set()
        for word in words:
            if word in self.SINGLE_DOMAIN_KEYWORDS:
                domain = self.SINGLE_DOMAIN_KEYWORDS[word]
                if domain not in seen:
                    domains.append(domain)
                    seen.add(domain)
        
        return domains if domains else [SemanticDomain.UTILITY]

    def _extract_semantic_types(self, words: List[str]) -> List[SemanticType]:
        """Extract semantic types from query words."""
        types: List[SemanticType] = []
        seen = set()
        for word in words:
            if word in self.SEMANTIC_TYPE_KEYWORDS:
                sem_type = self.SEMANTIC_TYPE_KEYWORDS[word]
                if sem_type not in seen:
                    types.append(sem_type)
                    seen.add(sem_type)
        
        return types if types else [SemanticType.GENERIC]

    def _extract_operations(self, words: List[str]) -> List[SemanticOperation]:
        """Extract required operations from words."""
        operations: List[SemanticOperation] = []
        
        op_keywords = {
            "validate": SemanticOperation.VALIDATE,
            "check": SemanticOperation.CHECK,
            "verify": SemanticOperation.VERIFY,
            "format": SemanticOperation.FORMAT,
            "convert": SemanticOperation.CONVERT,
            "transform": SemanticOperation.TRANSFORM,
            "parse": SemanticOperation.PARSE,
            "extract": SemanticOperation.EXTRACT,
            "sanitize": SemanticOperation.SANITIZE,
            "normalize": SemanticOperation.NORMALIZE,
            "hash": SemanticOperation.HASH,
            "encode": SemanticOperation.ENCODE,
            "search": SemanticOperation.SEARCH,
            "filter": SemanticOperation.FILTER,
            "sort": SemanticOperation.SORT,
            "calculate": SemanticOperation.CALCULATE,
        }
        
        seen = set()
        for word in words:
            if word in op_keywords and word not in seen:
                operations.append(op_keywords[word])
                seen.add(word)
        
        return operations

    def _determine_flow(self, domains: List[SemanticDomain]) -> str:
        """Determine the expected data flow."""
        if len(domains) <= 1:
            return "single"
        
        if SemanticDomain.VALIDATION in domains and SemanticDomain.FORMATTING in domains:
            return "validate_then_format"
        
        if SemanticDomain.PARSING in domains:
            return "parse_first"
        
        return "sequential"


class SemanticComposer:
    """
    Composes block graphs using semantic intent matching.
    
    This is the CORRECT way to compose blocks:
    1. Parse query into semantic requirements
    2. Find blocks matching each required domain
    3. Validate type flow between blocks
    4. Order by operation semantics
    5. Return validated graph
    """

    def __init__(self):
        self._semantic_index: Dict[str, SemanticIndexEntry] = {}
        self._domain_index: Dict[SemanticDomain, Set[str]] = {}
        self._operation_index: Dict[SemanticOperation, Set[str]] = {}
        self._semantic_type_index: Dict[SemanticType, Set[str]] = {}
        self._query_parser = QueryIntentParser()
        self._verified_block_ids: Optional[Set[str]] = None
    
    def set_verified_blocks(self, verified_ids: Set[str]) -> None:
        """Set the list of verified block IDs. Only these will be used in composition."""
        self._verified_block_ids = verified_ids
    
    def clear_verified_filter(self) -> None:
        """Clear the verified filter to use all blocks."""
        self._verified_block_ids = None

    def index_block(self, entry: SemanticIndexEntry) -> None:
        """Index a block for semantic search."""
        self._semantic_index[entry.block_identity] = entry
        
        domain = entry.semantic_intent.domain
        if domain not in self._domain_index:
            self._domain_index[domain] = set()
        self._domain_index[domain].add(entry.block_identity)
        
        operation = entry.semantic_intent.operation
        if operation not in self._operation_index:
            self._operation_index[operation] = set()
        self._operation_index[operation].add(entry.block_identity)
        
        for sem_type in entry.semantic_intent.input_semantic_types:
            if sem_type not in self._semantic_type_index:
                self._semantic_type_index[sem_type] = set()
            self._semantic_type_index[sem_type].add(entry.block_identity)
        for sem_type in entry.semantic_intent.output_semantic_types:
            if sem_type not in self._semantic_type_index:
                self._semantic_type_index[sem_type] = set()
            self._semantic_type_index[sem_type].add(entry.block_identity)

    def compose(
        self,
        query: str,
        min_trust: float = 0.2,
        max_nodes: int = 10,
    ) -> SemanticGraph:
        """
        Compose a semantic graph for the given query.
        
        This is the CORRECT composition logic:
        1. Parse query into semantic requirements
        2. Find best blocks for each required domain
        3. Validate connections between blocks
        4. Return validated graph
        """
        intent_analysis = self._query_parser.parse(query)
        
        required_domains = intent_analysis["required_domains"]
        required_types = intent_analysis["required_semantic_types"]
        
        import re
        query_words = list(set(re.sub(r'[^\w\s]', '', w).lower() for w in query.split() if len(w) >= 3))
        
        selected_blocks: List[SemanticIndexEntry] = []
        why_selected: Dict[str, str] = {}
        
        for domain in required_domains:
            domain_blocks = self._find_blocks_for_domain(
                domain, required_types, min_trust, query_words
            )
            
            for block in domain_blocks[:3]:
                if block.block_identity not in [b.block_identity for b in selected_blocks]:
                    selected_blocks.append(block)
                    why_selected[block.block_identity] = f"Matches domain: {domain.value}"
        
        selected_blocks = self._order_by_operation(selected_blocks)
        
        nodes: List[CompositionNode] = []
        edges: List[Tuple[str, str, str]] = []
        validation_notes: List[str] = []
        
        for i, block in enumerate(selected_blocks[:max_nodes]):
            input_sources: List[str] = []
            output_targets: List[str] = []
            
            if i > 0:
                prev_block = selected_blocks[i - 1]
                
                is_compatible = self._check_semantic_compatibility(prev_block, block)
                
                if is_compatible:
                    input_sources.append(prev_block.block_identity)
                    edges.append((
                        prev_block.block_identity,
                        block.block_identity,
                        "semantic_flow"
                    ))
                else:
                    validation_notes.append(
                        f"Semantic gap between {prev_block.name} and {block.name}: "
                        f"{prev_block.semantic_intent.domain.value} -> {block.semantic_intent.domain.value}"
                    )
            
            node = CompositionNode(
                block_identity=block.block_identity,
                block_name=block.name,
                semantic_intent=block.semantic_intent,
                position=i,
                why_selected=why_selected.get(block.block_identity, "Domain match"),
                input_sources=tuple(input_sources),
                output_targets=tuple(output_targets),
            )
            nodes.append(node)
        
        if nodes:
            total_trust = sum(b.trust_score for b in selected_blocks[:max_nodes]) / len(nodes)
        else:
            total_trust = 0.0
        
        is_valid = len(validation_notes) == 0 and len(nodes) > 0
        
        composition_confidence = self._calculate_confidence(
            nodes, edges, required_domains, validation_notes
        )
        
        return SemanticGraph(
            query=query,
            intent_analysis=intent_analysis,
            nodes=tuple(nodes),
            edges=tuple(edges),
            is_valid=is_valid,
            validation_details=tuple(validation_notes),
            total_trust_score=total_trust,
            composition_confidence=composition_confidence,
        )

    def _find_blocks_for_domain(
        self,
        domain: SemanticDomain,
        required_types: List[SemanticType],
        min_trust: float,
        query_words: Optional[List[str]] = None,
    ) -> List[SemanticIndexEntry]:
        """Find blocks matching a semantic domain, with text matching against query words."""
        block_ids = self._domain_index.get(domain, set())
        
        if not block_ids:
            fallback_domains = self._get_fallback_domains(domain)
            for fallback in fallback_domains:
                block_ids = self._domain_index.get(fallback, set())
                if block_ids:
                    break
        
        if self._verified_block_ids is not None:
            block_ids = block_ids.intersection(self._verified_block_ids)
        
        candidates: List[SemanticIndexEntry] = []
        for block_id in block_ids:
            entry = self._semantic_index.get(block_id)
            if entry and entry.trust_score >= min_trust:
                candidates.append(entry)
        
        def score_block(block: SemanticIndexEntry) -> float:
            score = block.trust_score
            for req_type in required_types:
                if req_type in block.semantic_intent.input_semantic_types:
                    score += 0.2
                if req_type in block.semantic_intent.output_semantic_types:
                    score += 0.1
            if block.is_pure:
                score += 0.1
            if block.is_deterministic:
                score += 0.1
            
            if query_words:
                block_name_lower = block.name.lower()
                block_desc_lower = block.description.lower() if block.description else ""
                block_category_lower = block.category.lower() if block.category else ""
                
                text_bonus = 0.0
                for word in query_words:
                    word_lower = word.lower()
                    if len(word_lower) < 3:
                        continue
                    if word_lower in block_name_lower:
                        text_bonus += 2.0
                    if word_lower in block_desc_lower:
                        text_bonus += 0.5
                    if word_lower in block_category_lower:
                        text_bonus += 0.3
                
                score += min(text_bonus, 5.0)
            
            return score
        
        candidates.sort(key=score_block, reverse=True)
        return candidates

    def _order_by_operation(
        self,
        blocks: List[SemanticIndexEntry]
    ) -> List[SemanticIndexEntry]:
        """Order blocks by their operation semantics."""
        def get_order(block: SemanticIndexEntry) -> int:
            return get_operation_order(block.semantic_intent.operation)
        
        return sorted(blocks, key=get_order)

    def _check_semantic_compatibility(
        self,
        source: SemanticIndexEntry,
        target: SemanticIndexEntry
    ) -> bool:
        """Check if source output is semantically compatible with target input."""
        if can_chain(source.semantic_intent, target.semantic_intent):
            return True
        
        if are_semantic_types_compatible(
            source.semantic_intent.output_semantic_types,
            target.semantic_intent.input_semantic_types
        ):
            return True
        
        for out_type in source.output_data_types:
            for in_type in target.input_data_types:
                if out_type == in_type:
                    return True
                if out_type == "any" or in_type == "any":
                    return True
        
        return False

    def _calculate_confidence(
        self,
        nodes: List[CompositionNode],
        edges: List[Tuple[str, str, str]],
        required_domains: List[SemanticDomain],
        validation_notes: List[str],
    ) -> float:
        """Calculate composition confidence score."""
        if not nodes:
            return 0.0
        
        covered_domains = set()
        for node in nodes:
            covered_domains.add(node.semantic_intent.domain)
        
        domain_coverage = len(covered_domains.intersection(set(required_domains))) / len(required_domains)
        
        expected_edges = len(nodes) - 1
        actual_edges = len(edges)
        edge_ratio = actual_edges / expected_edges if expected_edges > 0 else 1.0
        
        error_penalty = 0.1 * len(validation_notes)
        
        confidence = (domain_coverage * 0.5 + edge_ratio * 0.5) - error_penalty
        
        return max(0.0, min(1.0, confidence))

    def _get_fallback_domains(self, domain: SemanticDomain) -> List[SemanticDomain]:
        """Get fallback domains when primary domain has no blocks."""
        fallback_map = {
            SemanticDomain.FORMATTING: [SemanticDomain.STRING, SemanticDomain.TRANSFORMATION],
            SemanticDomain.PARSING: [SemanticDomain.STRING, SemanticDomain.TRANSFORMATION],
            SemanticDomain.ENCODING: [SemanticDomain.TRANSFORMATION, SemanticDomain.STRING],
            SemanticDomain.HASHING: [SemanticDomain.SECURITY, SemanticDomain.ENCODING],
            SemanticDomain.SECURITY: [SemanticDomain.VALIDATION, SemanticDomain.TRANSFORMATION],
            SemanticDomain.AUTHENTICATION: [SemanticDomain.SECURITY, SemanticDomain.VALIDATION],
            SemanticDomain.AGGREGATION: [SemanticDomain.COLLECTION, SemanticDomain.CALCULATION],
            SemanticDomain.SEARCHING: [SemanticDomain.FILTERING, SemanticDomain.COLLECTION],
            SemanticDomain.SORTING: [SemanticDomain.COLLECTION, SemanticDomain.FILTERING],
            SemanticDomain.COMPARISON: [SemanticDomain.VALIDATION, SemanticDomain.CALCULATION],
            SemanticDomain.NUMERIC: [SemanticDomain.CALCULATION, SemanticDomain.TRANSFORMATION],
            SemanticDomain.DATETIME: [SemanticDomain.STRING, SemanticDomain.CALCULATION],
        }
        return fallback_map.get(domain, [SemanticDomain.UTILITY])

    def get_blocks_by_domain(self, domain: SemanticDomain) -> List[SemanticIndexEntry]:
        """Get all blocks in a semantic domain."""
        block_ids = self._domain_index.get(domain, set())
        return [self._semantic_index[bid] for bid in block_ids if bid in self._semantic_index]

    def get_statistics(self) -> Dict[str, Any]:
        """Get semantic index statistics."""
        return {
            "total_blocks": len(self._semantic_index),
            "domains": {d.value: len(ids) for d, ids in self._domain_index.items()},
            "operations": {o.value: len(ids) for o, ids in self._operation_index.items()},
            "semantic_types": {t.value: len(ids) for t, ids in self._semantic_type_index.items()},
        }
