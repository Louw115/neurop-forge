"""
Deduplication Report - Generate human-readable reports.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from neurop_forge.deduplication.signature_hasher import SignatureHasher, DuplicateGroup
from neurop_forge.deduplication.policy_engine import PolicyDecision, DeduplicationPolicy
from neurop_forge.deduplication.dedup_processor import ProcessingResult


class DeduplicationReport:
    """Generate reports from deduplication results."""
    
    def __init__(
        self,
        hasher: SignatureHasher,
        result: ProcessingResult
    ):
        self.hasher = hasher
        self.result = result
    
    def generate_summary(self) -> str:
        """Generate a summary report."""
        lines = []
        lines.append("=" * 70)
        lines.append("  NEUROP FORGE V2 - DEDUPLICATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append("[SUMMARY]")
        lines.append("-" * 40)
        lines.append(f"  Original Blocks:    {self.result.original_count}")
        lines.append(f"  Final Blocks:       {self.result.final_count}")
        lines.append(f"  Duplicates Found:   {self.result.duplicates_found}")
        lines.append(f"  Blocks Removed:     {self.result.blocks_removed}")
        lines.append(f"  Blocks Renamed:     {self.result.blocks_renamed}")
        lines.append(f"  Reduction:          {self.result.reduction_percent:.1f}%")
        lines.append("")
        
        stats = self.hasher.get_statistics()
        lines.append("[DUPLICATE ANALYSIS]")
        lines.append("-" * 40)
        lines.append(f"  Unique Block Names:     {stats['unique_names']}")
        lines.append(f"  Names with Duplicates:  {stats['duplicate_names']}")
        lines.append(f"  Signature Conflicts:    {stats['signature_conflicts']}")
        lines.append(f"  Exact Duplicates:       {stats['exact_duplicates']}")
        lines.append(f"  Total Blocks Affected:  {stats['blocks_affected']}")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_detailed_report(self, max_groups: int = 20) -> str:
        """Generate a detailed report with duplicate groups."""
        lines = [self.generate_summary()]
        
        lines.append("[DUPLICATE GROUPS]")
        lines.append("-" * 40)
        
        duplicates = self.hasher.find_all_duplicates()
        
        for i, group in enumerate(duplicates[:max_groups]):
            lines.append(f"\n  [{i+1}] '{group.name}' - {group.count} variants")
            
            if group.has_signature_conflict:
                lines.append("      Status: SIGNATURE CONFLICT (different parameters)")
            else:
                lines.append("      Status: EXACT DUPLICATES (same parameters)")
            
            variants = group.get_variants()
            for sig, blocks in variants.items():
                lines.append(f"      Signature: {sig}")
                for block in blocks[:2]:
                    source = block.source_file.split("/")[-1] if "/" in block.source_file else block.source_file
                    lines.append(f"        - {block.block_id[:12]}... (score: {block.trust_score:.3f}, source: {source})")
        
        if len(duplicates) > max_groups:
            lines.append(f"\n  ... and {len(duplicates) - max_groups} more duplicate groups")
        
        lines.append("")
        lines.append("[POLICY DECISIONS]")
        lines.append("-" * 40)
        
        for decision in self.result.decisions[:20]:
            lines.append(f"  {decision.group_name}: {decision.policy_applied.value}")
            if decision.kept_block_id:
                lines.append(f"    Kept: {decision.kept_block_id[:12]}...")
            if decision.removed_count:
                lines.append(f"    Removed: {decision.removed_count} blocks")
        
        if len(self.result.decisions) > 20:
            lines.append(f"\n  ... and {len(self.result.decisions) - 20} more decisions")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"  DEDUPLICATION COMPLETE: {self.result.original_count} -> {self.result.final_count} blocks")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> Dict[str, Any]:
        """Generate a JSON-serializable report."""
        stats = self.hasher.get_statistics()
        
        return {
            "summary": {
                "original_count": self.result.original_count,
                "final_count": self.result.final_count,
                "duplicates_found": self.result.duplicates_found,
                "blocks_removed": self.result.blocks_removed,
                "blocks_renamed": self.result.blocks_renamed,
                "reduction_percent": round(self.result.reduction_percent, 2),
            },
            "analysis": stats,
            "decisions": [
                {
                    "group": d.group_name,
                    "policy": d.policy_applied.value,
                    "kept": d.kept_block_id,
                    "removed": d.removed_count,
                }
                for d in self.result.decisions
            ],
            "errors": self.result.errors,
        }
