"""
Policy Engine - Decide how to handle duplicate blocks.

Policies:
- KEEP_BEST: Keep only the highest-scoring block, remove others
- NAMESPACE: Rename duplicates with source-based namespaces
- MERGE: Combine into one block with aliased parameters (future)
- QUARANTINE: Move duplicates to quarantine for manual review
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from neurop_forge.deduplication.signature_hasher import (
    BlockSignature,
    DuplicateGroup,
)


class DeduplicationPolicy(Enum):
    """How to handle duplicate blocks."""
    KEEP_BEST = "keep_best"
    NAMESPACE = "namespace"
    QUARANTINE = "quarantine"
    KEEP_ALL = "keep_all"


@dataclass
class DeduplicationAction:
    """Action to take on a specific block."""
    block_id: str
    original_name: str
    action: str
    new_name: Optional[str] = None
    reason: str = ""


@dataclass
class PolicyDecision:
    """Decision made by policy engine for a duplicate group."""
    group_name: str
    policy_applied: DeduplicationPolicy
    actions: List[DeduplicationAction] = field(default_factory=list)
    kept_block_id: Optional[str] = None
    removed_count: int = 0


class PolicyEngine:
    """Applies deduplication policies to resolve duplicate blocks."""
    
    def __init__(self, default_policy: DeduplicationPolicy = DeduplicationPolicy.KEEP_BEST):
        self.default_policy = default_policy
        self._decisions: List[PolicyDecision] = []
    
    def _extract_namespace(self, source_file: str) -> str:
        """Extract a namespace from source file path."""
        if not source_file:
            return "unknown"
        
        filename = source_file.split("/")[-1] if "/" in source_file else source_file
        name = filename.replace(".py", "").replace("_", ".")
        
        parts = name.split(".")
        if len(parts) > 1:
            return parts[0]
        return name
    
    def apply_keep_best(self, group: DuplicateGroup) -> PolicyDecision:
        """Keep only the highest-scoring block."""
        decision = PolicyDecision(
            group_name=group.name,
            policy_applied=DeduplicationPolicy.KEEP_BEST
        )
        
        best = group.get_best_block()
        decision.kept_block_id = best.block_id
        
        for block in group.blocks:
            if block.block_id == best.block_id:
                decision.actions.append(DeduplicationAction(
                    block_id=block.block_id,
                    original_name=block.name,
                    action="keep",
                    reason=f"Highest trust score ({block.trust_score:.3f})"
                ))
            else:
                decision.actions.append(DeduplicationAction(
                    block_id=block.block_id,
                    original_name=block.name,
                    action="remove",
                    reason=f"Lower trust score ({block.trust_score:.3f}) than best"
                ))
                decision.removed_count += 1
        
        return decision
    
    def apply_namespace(self, group: DuplicateGroup) -> PolicyDecision:
        """Rename blocks with source-based namespaces."""
        decision = PolicyDecision(
            group_name=group.name,
            policy_applied=DeduplicationPolicy.NAMESPACE
        )
        
        namespaces_used = {}
        
        for block in group.blocks:
            namespace = self._extract_namespace(block.source_file)
            
            if namespace in namespaces_used:
                counter = 2
                while f"{namespace}{counter}" in namespaces_used:
                    counter += 1
                namespace = f"{namespace}{counter}"
            
            namespaces_used[namespace] = block.block_id
            new_name = f"{namespace}.{block.name}"
            
            decision.actions.append(DeduplicationAction(
                block_id=block.block_id,
                original_name=block.name,
                action="rename",
                new_name=new_name,
                reason=f"Namespaced from {block.source_file}"
            ))
        
        return decision
    
    def apply_quarantine(self, group: DuplicateGroup) -> PolicyDecision:
        """Move all duplicates to quarantine."""
        decision = PolicyDecision(
            group_name=group.name,
            policy_applied=DeduplicationPolicy.QUARANTINE
        )
        
        for block in group.blocks:
            decision.actions.append(DeduplicationAction(
                block_id=block.block_id,
                original_name=block.name,
                action="quarantine",
                reason="Manual review required for duplicate resolution"
            ))
            decision.removed_count += 1
        
        return decision
    
    def apply_keep_all(self, group: DuplicateGroup) -> PolicyDecision:
        """Keep all blocks (no deduplication, for comparison)."""
        decision = PolicyDecision(
            group_name=group.name,
            policy_applied=DeduplicationPolicy.KEEP_ALL
        )
        
        for block in group.blocks:
            decision.actions.append(DeduplicationAction(
                block_id=block.block_id,
                original_name=block.name,
                action="keep",
                reason="Policy: keep all variants"
            ))
        
        return decision
    
    def process_group(
        self,
        group: DuplicateGroup,
        policy: Optional[DeduplicationPolicy] = None
    ) -> PolicyDecision:
        """Apply a policy to a duplicate group."""
        policy = policy or self.default_policy
        
        if policy == DeduplicationPolicy.KEEP_BEST:
            decision = self.apply_keep_best(group)
        elif policy == DeduplicationPolicy.NAMESPACE:
            decision = self.apply_namespace(group)
        elif policy == DeduplicationPolicy.QUARANTINE:
            decision = self.apply_quarantine(group)
        else:
            decision = self.apply_keep_all(group)
        
        self._decisions.append(decision)
        return decision
    
    def process_all_groups(
        self,
        groups: List[DuplicateGroup],
        policy: Optional[DeduplicationPolicy] = None
    ) -> List[PolicyDecision]:
        """Process all duplicate groups."""
        decisions = []
        for group in groups:
            decision = self.process_group(group, policy)
            decisions.append(decision)
        return decisions
    
    def get_removal_list(self) -> List[str]:
        """Get list of block IDs to remove."""
        removals = []
        for decision in self._decisions:
            for action in decision.actions:
                if action.action in ("remove", "quarantine"):
                    removals.append(action.block_id)
        return removals
    
    def get_rename_map(self) -> Dict[str, str]:
        """Get map of block_id -> new_name for renames."""
        renames = {}
        for decision in self._decisions:
            for action in decision.actions:
                if action.action == "rename" and action.new_name:
                    renames[action.block_id] = action.new_name
        return renames
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get policy application statistics."""
        total_removed = sum(d.removed_count for d in self._decisions)
        total_renamed = len(self.get_rename_map())
        
        return {
            "groups_processed": len(self._decisions),
            "blocks_removed": total_removed,
            "blocks_renamed": total_renamed,
            "policy_breakdown": {
                p.value: sum(1 for d in self._decisions if d.policy_applied == p)
                for p in DeduplicationPolicy
            }
        }
