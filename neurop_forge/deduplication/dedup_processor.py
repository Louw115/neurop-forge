"""
Deduplication Processor - Orchestrates the full deduplication pipeline.

Loads blocks, detects duplicates, applies policies, and outputs results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from neurop_forge.deduplication.signature_hasher import SignatureHasher, DuplicateGroup
from neurop_forge.deduplication.policy_engine import (
    PolicyEngine,
    DeduplicationPolicy,
    PolicyDecision,
)


@dataclass
class ProcessingResult:
    """Result of deduplication processing."""
    original_count: int = 0
    final_count: int = 0
    duplicates_found: int = 0
    blocks_removed: int = 0
    blocks_renamed: int = 0
    decisions: List[PolicyDecision] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def reduction_percent(self) -> float:
        if self.original_count == 0:
            return 0.0
        return (self.blocks_removed / self.original_count) * 100


class DeduplicationProcessor:
    """Main processor for block deduplication."""
    
    def __init__(
        self,
        library_path: str = ".neurop_expanded_library",
        output_path: str = ".neurop_deduplicated_library",
        policy: DeduplicationPolicy = DeduplicationPolicy.KEEP_BEST
    ):
        self.library_path = Path(library_path)
        self.output_path = Path(output_path)
        self.policy = policy
        
        self._hasher = SignatureHasher()
        self._policy_engine = PolicyEngine(default_policy=policy)
        self._blocks: Dict[str, Dict] = {}
        self._result = ProcessingResult()
    
    def load_blocks(self) -> int:
        """Load all blocks from the library."""
        if not self.library_path.exists():
            self._result.errors.append(f"Library path not found: {self.library_path}")
            return 0
        
        count = 0
        for block_file in self.library_path.glob("*.json"):
            try:
                with open(block_file) as f:
                    block_data = json.load(f)
                
                block_id = block_data.get("identity", {}).get("hash_value", block_file.stem)
                self._blocks[block_id] = block_data
                self._hasher.add_block(block_data)
                count += 1
            except Exception as e:
                self._result.errors.append(f"Error loading {block_file}: {e}")
        
        self._result.original_count = count
        return count
    
    def detect_duplicates(self) -> List[DuplicateGroup]:
        """Detect all duplicate block names."""
        duplicates = self._hasher.find_all_duplicates()
        self._result.duplicates_found = len(duplicates)
        return duplicates
    
    def apply_policy(
        self,
        duplicates: List[DuplicateGroup],
        policy: Optional[DeduplicationPolicy] = None
    ) -> List[PolicyDecision]:
        """Apply deduplication policy to all duplicates."""
        policy = policy or self.policy
        decisions = self._policy_engine.process_all_groups(duplicates, policy)
        self._result.decisions = decisions
        return decisions
    
    def execute_decisions(self) -> int:
        """Execute the policy decisions and create deduplicated library."""
        removal_list = set(self._policy_engine.get_removal_list())
        rename_map = self._policy_engine.get_rename_map()
        
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        kept_count = 0
        for block_id, block_data in self._blocks.items():
            if block_id in removal_list:
                self._result.blocks_removed += 1
                continue
            
            if block_id in rename_map:
                new_name = rename_map[block_id]
                old_name = block_data["metadata"].get("name", "")
                block_data["metadata"]["original_name"] = old_name
                block_data["metadata"]["name"] = new_name
                self._result.blocks_renamed += 1
            
            output_file = self.output_path / f"{block_id[:16]}.json"
            try:
                with open(output_file, "w") as f:
                    json.dump(block_data, f, indent=2)
                kept_count += 1
            except Exception as e:
                self._result.errors.append(f"Error writing {output_file}: {e}")
        
        self._result.final_count = kept_count
        return kept_count
    
    def run(self, execute: bool = False) -> ProcessingResult:
        """Run the full deduplication pipeline."""
        self.load_blocks()
        duplicates = self.detect_duplicates()
        self.apply_policy(duplicates)
        
        if execute:
            self.execute_decisions()
        else:
            stats = self._policy_engine.get_statistics()
            self._result.blocks_removed = stats["blocks_removed"]
            self._result.blocks_renamed = stats["blocks_renamed"]
            self._result.final_count = self._result.original_count - self._result.blocks_removed
        
        return self._result
    
    def get_hasher(self) -> SignatureHasher:
        """Get the signature hasher for inspection."""
        return self._hasher
    
    def get_policy_engine(self) -> PolicyEngine:
        """Get the policy engine for inspection."""
        return self._policy_engine


def run_deduplication(
    library_path: str = ".neurop_expanded_library",
    output_path: str = ".neurop_deduplicated_library",
    policy: DeduplicationPolicy = DeduplicationPolicy.KEEP_BEST,
    execute: bool = False
) -> ProcessingResult:
    """Convenience function to run deduplication."""
    processor = DeduplicationProcessor(library_path, output_path, policy)
    return processor.run(execute=execute)
