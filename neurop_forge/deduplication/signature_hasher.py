"""
Signature Hasher - Detect duplicate blocks by hashing their signatures.

A block's signature is: name + sorted parameter names/types
Two blocks with the same name but different signatures are duplicates.
"""

import hashlib
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class BlockSignature:
    """Represents a block's unique signature."""
    block_id: str
    name: str
    param_signature: str
    source_file: str
    trust_score: float
    full_hash: str
    
    @property
    def is_complete(self) -> bool:
        return bool(self.name and self.param_signature)


@dataclass
class DuplicateGroup:
    """A group of blocks that share the same name."""
    name: str
    blocks: List[BlockSignature] = field(default_factory=list)
    
    @property
    def count(self) -> int:
        return len(self.blocks)
    
    @property
    def has_signature_conflict(self) -> bool:
        """True if blocks have different parameter signatures."""
        if len(self.blocks) < 2:
            return False
        sigs = set(b.param_signature for b in self.blocks)
        return len(sigs) > 1
    
    @property
    def has_exact_duplicates(self) -> bool:
        """True if blocks have identical signatures (true duplicates)."""
        if len(self.blocks) < 2:
            return False
        sigs = [b.param_signature for b in self.blocks]
        return len(sigs) != len(set(sigs))
    
    def get_best_block(self) -> BlockSignature:
        """Return the block with highest trust score."""
        return max(self.blocks, key=lambda b: b.trust_score)
    
    def get_variants(self) -> Dict[str, List[BlockSignature]]:
        """Group blocks by their parameter signature."""
        variants = defaultdict(list)
        for block in self.blocks:
            variants[block.param_signature].append(block)
        return dict(variants)


class SignatureHasher:
    """Generates and compares block signatures to detect duplicates."""
    
    def __init__(self):
        self._signatures: Dict[str, BlockSignature] = {}
        self._name_groups: Dict[str, DuplicateGroup] = {}
    
    def compute_signature(self, block_data: Dict[str, Any]) -> BlockSignature:
        """Compute a unique signature for a block."""
        identity = block_data.get("identity", {})
        metadata = block_data.get("metadata", {})
        interface = block_data.get("interface", {})
        trust = block_data.get("trust_score", {})
        
        block_id = identity.get("hash_value", "")
        name = metadata.get("name", "")
        source_file = metadata.get("source_file", "")
        trust_score = trust.get("overall_score", 0.0)
        
        inputs = interface.get("inputs", [])
        params = []
        for idx, inp in enumerate(inputs):
            param_name = inp.get("name", "")
            param_type = inp.get("data_type", "any")
            params.append(f"{idx}:{param_name}:{param_type}")
        
        param_signature = "|".join(params) if params else "void"
        
        sig_string = f"{name}:{param_signature}"
        full_hash = hashlib.sha256(sig_string.encode()).hexdigest()[:16]
        
        return BlockSignature(
            block_id=block_id,
            name=name,
            param_signature=param_signature,
            source_file=source_file,
            trust_score=trust_score,
            full_hash=full_hash
        )
    
    def add_block(self, block_data: Dict[str, Any]) -> BlockSignature:
        """Add a block and compute its signature."""
        sig = self.compute_signature(block_data)
        self._signatures[sig.block_id] = sig
        
        if sig.name:
            if sig.name not in self._name_groups:
                self._name_groups[sig.name] = DuplicateGroup(name=sig.name)
            self._name_groups[sig.name].blocks.append(sig)
        
        return sig
    
    def find_all_duplicates(self) -> List[DuplicateGroup]:
        """Find all block names with multiple implementations."""
        duplicates = []
        for name, group in self._name_groups.items():
            if group.count > 1:
                duplicates.append(group)
        return sorted(duplicates, key=lambda g: -g.count)
    
    def find_signature_conflicts(self) -> List[DuplicateGroup]:
        """Find blocks with same name but different signatures."""
        conflicts = []
        for group in self.find_all_duplicates():
            if group.has_signature_conflict:
                conflicts.append(group)
        return conflicts
    
    def find_exact_duplicates(self) -> List[DuplicateGroup]:
        """Find blocks with same name AND same signature (true duplicates)."""
        exact = []
        for group in self.find_all_duplicates():
            if group.has_exact_duplicates:
                exact.append(group)
        return exact
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get duplicate detection statistics."""
        all_dups = self.find_all_duplicates()
        conflicts = self.find_signature_conflicts()
        exact = self.find_exact_duplicates()
        
        return {
            "total_blocks": len(self._signatures),
            "unique_names": len(self._name_groups),
            "duplicate_names": len(all_dups),
            "signature_conflicts": len(conflicts),
            "exact_duplicates": len(exact),
            "blocks_affected": sum(g.count for g in all_dups),
        }
