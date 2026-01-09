"""
AI fetch engine for block query resolution.

This module provides the interface for AI to:
- Search the library by intent
- Reason over block metadata
- Assemble block graphs
- Verify composition compatibility

AI is NOT allowed to:
- Write code
- Modify blocks
- Bypass trust rules
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import NeuropBlock
from neurop_forge.library.block_store import BlockStore
from neurop_forge.library.indexer import BlockIndexer, IndexEntry


class QueryType(Enum):
    """Type of AI query."""
    INTENT_SEARCH = "intent_search"
    CATEGORY_SEARCH = "category_search"
    COMPOSE_GRAPH = "compose_graph"
    VERIFY_COMPATIBILITY = "verify_compatibility"


@dataclass
class BlockNode:
    """A node in a block graph."""
    block_identity: str
    block_name: str
    intent: str
    position: int
    input_connections: Tuple[str, ...]
    output_connections: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "block_name": self.block_name,
            "intent": self.intent,
            "position": self.position,
            "input_connections": list(self.input_connections),
            "output_connections": list(self.output_connections),
        }


@dataclass
class BlockGraph:
    """
    A graph of connected NeuropBlocks.
    
    This is what AI returns instead of code - a verified assembly
    of validated blocks.
    """
    query: str
    nodes: Tuple[BlockNode, ...]
    edges: Tuple[Tuple[str, str], ...]
    is_valid: bool
    validation_notes: Tuple[str, ...]
    total_trust_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [list(e) for e in self.edges],
            "is_valid": self.is_valid,
            "validation_notes": list(self.validation_notes),
            "total_trust_score": self.total_trust_score,
        }

    def get_execution_order(self) -> List[str]:
        """Get block identities in execution order."""
        return [node.block_identity for node in sorted(self.nodes, key=lambda n: n.position)]


@dataclass
class FetchResult:
    """Result of an AI fetch query."""
    query_type: QueryType
    query: str
    blocks_found: Tuple[IndexEntry, ...]
    graph: Optional[BlockGraph]
    metadata: Dict[str, Any]
    success: bool
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_type": self.query_type.value,
            "query": self.query,
            "blocks_found": [b.to_dict() for b in self.blocks_found],
            "graph": self.graph.to_dict() if self.graph else None,
            "metadata": self.metadata,
            "success": self.success,
            "message": self.message,
        }


class FetchEngine:
    """
    AI query resolution engine.
    
    This is the interface for AI to interact with the block library.
    AI can:
    - Search by intent
    - Reason over metadata
    - Request block graphs
    - Verify compatibility
    
    AI cannot:
    - Access raw code (only normalized logic references)
    - Modify any blocks
    - Bypass trust requirements
    """

    MINIMUM_TRUST_FOR_FETCH = 0.2

    def __init__(
        self,
        store: BlockStore,
        indexer: BlockIndexer,
    ):
        self._store = store
        self._indexer = indexer

    def search_by_intent(
        self,
        intent: str,
        min_trust: float = 0.2,
        limit: int = 10,
    ) -> FetchResult:
        """
        Search for blocks by intent description.
        
        Args:
            intent: Natural language intent description
            min_trust: Minimum trust score (default 0.2)
            limit: Maximum results
            
        Returns:
            FetchResult with matching blocks
        """
        effective_min_trust = max(min_trust, self.MINIMUM_TRUST_FOR_FETCH)

        entries = self._indexer.search(
            query=intent,
            min_trust=effective_min_trust,
            limit=limit,
        )

        return FetchResult(
            query_type=QueryType.INTENT_SEARCH,
            query=intent,
            blocks_found=tuple(entries),
            graph=None,
            metadata={
                "total_matching": len(entries),
                "min_trust_applied": effective_min_trust,
            },
            success=len(entries) > 0,
            message=f"Found {len(entries)} blocks matching intent",
        )

    def search_by_category(
        self,
        category: str,
        min_trust: float = 0.2,
    ) -> FetchResult:
        """
        Search for blocks by category.
        
        Args:
            category: Block category
            min_trust: Minimum trust score
            
        Returns:
            FetchResult with matching blocks
        """
        effective_min_trust = max(min_trust, self.MINIMUM_TRUST_FOR_FETCH)

        entries = self._indexer.search_by_category(
            category=category,
            min_trust=effective_min_trust,
        )

        return FetchResult(
            query_type=QueryType.CATEGORY_SEARCH,
            query=category,
            blocks_found=tuple(entries),
            graph=None,
            metadata={
                "category": category,
                "total_matching": len(entries),
            },
            success=len(entries) > 0,
            message=f"Found {len(entries)} blocks in category '{category}'",
        )

    def compose_graph(
        self,
        intent: str,
        required_capabilities: Optional[List[str]] = None,
    ) -> FetchResult:
        """
        Compose a block graph for a given intent.
        
        This returns a graph structure, NOT code.
        
        Args:
            intent: The high-level intent to fulfill
            required_capabilities: Optional list of required block capabilities
            
        Returns:
            FetchResult with a BlockGraph if successful
        """
        keywords = intent.lower().split()

        all_entries: List[IndexEntry] = []

        for keyword in keywords:
            entries = self._indexer.search(
                query=keyword,
                min_trust=self.MINIMUM_TRUST_FOR_FETCH,
                limit=5,
            )
            all_entries.extend(entries)

        seen_ids: Set[str] = set()
        unique_entries: List[IndexEntry] = []
        for entry in all_entries:
            if entry.block_identity not in seen_ids:
                seen_ids.add(entry.block_identity)
                unique_entries.append(entry)

        unique_entries.sort(key=lambda e: e.trust_score, reverse=True)

        if not unique_entries:
            return FetchResult(
                query_type=QueryType.COMPOSE_GRAPH,
                query=intent,
                blocks_found=(),
                graph=None,
                metadata={},
                success=False,
                message="No blocks found for intent",
            )

        nodes: List[BlockNode] = []
        edges: List[Tuple[str, str]] = []
        validation_notes: List[str] = []

        for i, entry in enumerate(unique_entries[:10]):
            input_connections: List[str] = []
            output_connections: List[str] = []

            if i > 0:
                prev_entry = unique_entries[i - 1]
                if self._check_type_compatibility(prev_entry, entry):
                    input_connections.append(prev_entry.block_identity)
                    edges.append((prev_entry.block_identity, entry.block_identity))
                else:
                    validation_notes.append(
                        f"Type mismatch between {prev_entry.name} and {entry.name}"
                    )

            node = BlockNode(
                block_identity=entry.block_identity,
                block_name=entry.name,
                intent=entry.intent,
                position=i,
                input_connections=tuple(input_connections),
                output_connections=tuple(output_connections),
            )
            nodes.append(node)

        total_trust = sum(e.trust_score for e in unique_entries[:10]) / len(unique_entries[:10])

        is_valid = len(validation_notes) == 0 and len(nodes) > 0

        graph = BlockGraph(
            query=intent,
            nodes=tuple(nodes),
            edges=tuple(edges),
            is_valid=is_valid,
            validation_notes=tuple(validation_notes),
            total_trust_score=total_trust,
        )

        return FetchResult(
            query_type=QueryType.COMPOSE_GRAPH,
            query=intent,
            blocks_found=tuple(unique_entries[:10]),
            graph=graph,
            metadata={
                "nodes_count": len(nodes),
                "edges_count": len(edges),
            },
            success=True,
            message=f"Composed graph with {len(nodes)} blocks",
        )

    def verify_compatibility(
        self,
        source_id: str,
        target_id: str,
    ) -> FetchResult:
        """
        Verify if two blocks are compatible for composition.
        
        Args:
            source_id: Source block identity
            target_id: Target block identity
            
        Returns:
            FetchResult with compatibility information
        """
        source_entry = self._indexer.get_entry(source_id)
        target_entry = self._indexer.get_entry(target_id)

        if not source_entry or not target_entry:
            return FetchResult(
                query_type=QueryType.VERIFY_COMPATIBILITY,
                query=f"{source_id} -> {target_id}",
                blocks_found=(),
                graph=None,
                metadata={},
                success=False,
                message="One or both blocks not found",
            )

        is_compatible = self._check_type_compatibility(source_entry, target_entry)

        return FetchResult(
            query_type=QueryType.VERIFY_COMPATIBILITY,
            query=f"{source_id} -> {target_id}",
            blocks_found=(source_entry, target_entry),
            graph=None,
            metadata={
                "source_outputs": list(source_entry.output_types),
                "target_inputs": list(target_entry.input_types),
                "compatible": is_compatible,
            },
            success=True,
            message="Compatible" if is_compatible else "Not compatible",
        )

    def _check_type_compatibility(
        self,
        source: IndexEntry,
        target: IndexEntry,
    ) -> bool:
        """Check if source output types match target input types."""
        if not source.output_types or not target.input_types:
            return True

        for output_type in source.output_types:
            for input_type in target.input_types:
                if output_type == input_type:
                    return True
                if output_type == "any" or input_type == "any":
                    return True

        return False

    def get_block_metadata(self, identity: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a block (no code access).
        
        Args:
            identity: Block identity
            
        Returns:
            Metadata dict or None
        """
        block = self._store.get(identity)
        if not block:
            return None

        if block.trust_score.overall_score < self.MINIMUM_TRUST_FOR_FETCH:
            return None

        return {
            "identity": identity,
            "name": block.metadata.name,
            "intent": block.metadata.intent,
            "description": block.metadata.description,
            "category": block.metadata.category,
            "tags": list(block.metadata.tags),
            "interface": block.interface.to_dict(),
            "constraints": {
                "purity": block.constraints.purity.value,
                "deterministic": block.constraints.deterministic,
            },
            "trust_score": block.trust_score.overall_score,
        }

    def get_available_categories(self) -> List[str]:
        """Get all available block categories."""
        return self._indexer.get_all_categories()
