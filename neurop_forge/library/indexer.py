"""
Block indexer for intent and constraint-based search.

This module provides indexing capabilities for fast block lookup by:
- Intent keywords
- Category
- Constraints (purity, determinism, etc.)
- Trust score
"""

import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from neurop_forge.core.block_schema import NeuropBlock, PurityLevel, DataType


@dataclass
class IndexEntry:
    """An entry in the block index."""
    block_identity: str
    name: str
    intent: str
    category: str
    keywords: Tuple[str, ...]
    input_types: Tuple[str, ...]
    output_types: Tuple[str, ...]
    is_pure: bool
    is_deterministic: bool
    trust_score: float
    language: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "name": self.name,
            "intent": self.intent,
            "category": self.category,
            "keywords": list(self.keywords),
            "input_types": list(self.input_types),
            "output_types": list(self.output_types),
            "is_pure": self.is_pure,
            "is_deterministic": self.is_deterministic,
            "trust_score": self.trust_score,
            "language": self.language,
        }


class BlockIndexer:
    """
    Indexer for NeuropBlock search and discovery.
    
    Provides fast lookup by:
    - Keyword search
    - Category filtering
    - Type matching
    - Constraint filtering
    - Trust score filtering
    """

    def __init__(self):
        self._entries: Dict[str, IndexEntry] = {}
        self._keyword_index: Dict[str, Set[str]] = defaultdict(set)
        self._category_index: Dict[str, Set[str]] = defaultdict(set)
        self._type_index: Dict[str, Set[str]] = defaultdict(set)
        self._purity_index: Dict[bool, Set[str]] = defaultdict(set)
        self._determinism_index: Dict[bool, Set[str]] = defaultdict(set)

    def index_block(self, block: NeuropBlock) -> IndexEntry:
        """
        Index a NeuropBlock for search.
        
        Args:
            block: The block to index
            
        Returns:
            IndexEntry for the block
        """
        identity = block.get_identity_hash()

        keywords = self._extract_keywords(block)
        input_types = tuple(p.data_type.value for p in block.interface.inputs)
        output_types = tuple(p.data_type.value for p in block.interface.outputs)

        entry = IndexEntry(
            block_identity=identity,
            name=block.metadata.name,
            intent=block.metadata.intent,
            category=block.metadata.category,
            keywords=keywords,
            input_types=input_types,
            output_types=output_types,
            is_pure=block.is_pure(),
            is_deterministic=block.is_deterministic(),
            trust_score=block.get_trust_level(),
            language=block.metadata.language,
        )

        self._entries[identity] = entry

        for keyword in keywords:
            self._keyword_index[keyword.lower()].add(identity)

        self._category_index[block.metadata.category].add(identity)

        for input_type in input_types:
            self._type_index[f"input:{input_type}"].add(identity)
        for output_type in output_types:
            self._type_index[f"output:{output_type}"].add(identity)

        self._purity_index[entry.is_pure].add(identity)
        self._determinism_index[entry.is_deterministic].add(identity)

        return entry

    def _extract_keywords(self, block: NeuropBlock) -> Tuple[str, ...]:
        """Extract searchable keywords from a block."""
        keywords: Set[str] = set()

        name_words = re.findall(r'[a-z]+', block.metadata.name.lower())
        keywords.update(name_words)

        keywords.update(t.lower() for t in block.metadata.tags)

        intent_words = re.findall(r'[a-z]+', block.metadata.intent.lower())
        keywords.update(w for w in intent_words if len(w) > 2)

        keywords.add(block.metadata.category)

        return tuple(sorted(keywords))

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_trust: float = 0.0,
        require_pure: bool = False,
        require_deterministic: bool = False,
        input_types: Optional[List[str]] = None,
        output_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[IndexEntry]:
        """
        Search for blocks matching criteria.
        
        Args:
            query: Search query (keywords)
            category: Optional category filter
            min_trust: Minimum trust score
            require_pure: Only return pure blocks
            require_deterministic: Only return deterministic blocks
            input_types: Required input types
            output_types: Required output types
            limit: Maximum results to return
            
        Returns:
            List of matching IndexEntry objects
        """
        candidate_ids: Optional[Set[str]] = None

        if query:
            query_words = query.lower().split()
            for word in query_words:
                word_matches = set()
                for keyword, ids in self._keyword_index.items():
                    if word in keyword or keyword in word:
                        word_matches.update(ids)

                if candidate_ids is None:
                    candidate_ids = word_matches
                else:
                    candidate_ids = candidate_ids.union(word_matches)

        if candidate_ids is None:
            candidate_ids = set(self._entries.keys())

        if category:
            category_ids = self._category_index.get(category, set())
            candidate_ids = candidate_ids.intersection(category_ids)

        if require_pure:
            pure_ids = self._purity_index.get(True, set())
            candidate_ids = candidate_ids.intersection(pure_ids)

        if require_deterministic:
            det_ids = self._determinism_index.get(True, set())
            candidate_ids = candidate_ids.intersection(det_ids)

        if input_types:
            for input_type in input_types:
                type_ids = self._type_index.get(f"input:{input_type}", set())
                candidate_ids = candidate_ids.intersection(type_ids)

        if output_types:
            for output_type in output_types:
                type_ids = self._type_index.get(f"output:{output_type}", set())
                candidate_ids = candidate_ids.intersection(type_ids)

        results = []
        for identity in candidate_ids:
            entry = self._entries.get(identity)
            if entry and entry.trust_score >= min_trust:
                results.append(entry)

        results.sort(key=lambda e: e.trust_score, reverse=True)

        return results[:limit]

    def search_by_intent(self, intent: str, limit: int = 10) -> List[IndexEntry]:
        """
        Search blocks by intent description.
        
        Args:
            intent: Intent description to match
            limit: Maximum results
            
        Returns:
            List of matching entries
        """
        return self.search(intent, limit=limit)

    def search_by_category(
        self,
        category: str,
        min_trust: float = 0.0,
    ) -> List[IndexEntry]:
        """
        Get all blocks in a category.
        
        Args:
            category: Category to filter by
            min_trust: Minimum trust score
            
        Returns:
            List of entries in category
        """
        ids = self._category_index.get(category, set())
        results = []
        for identity in ids:
            entry = self._entries.get(identity)
            if entry and entry.trust_score >= min_trust:
                results.append(entry)
        return sorted(results, key=lambda e: e.trust_score, reverse=True)

    def search_compatible(
        self,
        output_type: str,
        category: Optional[str] = None,
    ) -> List[IndexEntry]:
        """
        Search for blocks that can accept a given output type.
        
        Args:
            output_type: The output type to match against inputs
            category: Optional category filter
            
        Returns:
            List of compatible entries
        """
        type_ids = self._type_index.get(f"input:{output_type}", set())

        if category:
            category_ids = self._category_index.get(category, set())
            type_ids = type_ids.intersection(category_ids)

        return [self._entries[id] for id in type_ids if id in self._entries]

    def get_entry(self, identity: str) -> Optional[IndexEntry]:
        """Get index entry by identity."""
        return self._entries.get(identity)

    def get_all_categories(self) -> List[str]:
        """Get all indexed categories."""
        return list(self._category_index.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_entries": len(self._entries),
            "total_keywords": len(self._keyword_index),
            "categories": {
                cat: len(ids) for cat, ids in self._category_index.items()
            },
            "pure_blocks": len(self._purity_index.get(True, set())),
            "deterministic_blocks": len(self._determinism_index.get(True, set())),
        }

    def clear(self) -> None:
        """Clear all indexes."""
        self._entries.clear()
        self._keyword_index.clear()
        self._category_index.clear()
        self._type_index.clear()
        self._purity_index.clear()
        self._determinism_index.clear()
