"""
Copyright 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Block Tier Classification System

Tier-A: 100% deterministic, safe blocks
- Single-function, no external dependencies
- Verified with 100% success rate
- Pure functions with predictable outputs

Tier-B: Context-dependent blocks
- May require specific input formats
- Verified but with edge cases
- Useful but need care in composition
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import json
from pathlib import Path

from neurop_forge.core.block_schema import NeuropBlock, DataType


class BlockTier(Enum):
    TIER_A = "tier_a"
    TIER_B = "tier_b"
    UNCLASSIFIED = "unclassified"
    QUARANTINED = "quarantined"


@dataclass
class TierClassification:
    """Classification result for a block."""
    block_id: str
    block_name: str
    tier: BlockTier
    reasons: List[str]
    confidence: float
    input_complexity: int
    has_external_deps: bool
    is_pure_function: bool


@dataclass
class TierRegistry:
    """Registry of block tier classifications."""
    tier_a: Dict[str, TierClassification] = field(default_factory=dict)
    tier_b: Dict[str, TierClassification] = field(default_factory=dict)
    quarantined: Dict[str, TierClassification] = field(default_factory=dict)
    unclassified: Dict[str, TierClassification] = field(default_factory=dict)
    
    def get_tier(self, block_id: str) -> BlockTier:
        """Get the tier for a block."""
        if block_id in self.tier_a:
            return BlockTier.TIER_A
        elif block_id in self.tier_b:
            return BlockTier.TIER_B
        elif block_id in self.quarantined:
            return BlockTier.QUARANTINED
        return BlockTier.UNCLASSIFIED
    
    def get_tier_a_ids(self) -> Set[str]:
        """Get all Tier-A block IDs."""
        return set(self.tier_a.keys())
    
    def get_tier_b_ids(self) -> Set[str]:
        """Get all Tier-B block IDs."""
        return set(self.tier_b.keys())
    
    def summary(self) -> Dict[str, int]:
        """Get summary counts."""
        return {
            "tier_a": len(self.tier_a),
            "tier_b": len(self.tier_b),
            "quarantined": len(self.quarantined),
            "unclassified": len(self.unclassified),
            "total": len(self.tier_a) + len(self.tier_b) + len(self.quarantined) + len(self.unclassified),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        def classification_to_dict(c: TierClassification) -> Dict[str, Any]:
            return {
                "block_id": c.block_id,
                "block_name": c.block_name,
                "tier": c.tier.value,
                "reasons": c.reasons,
                "confidence": c.confidence,
                "input_complexity": c.input_complexity,
                "has_external_deps": c.has_external_deps,
                "is_pure_function": c.is_pure_function,
            }
        
        return {
            "tier_a": {k: classification_to_dict(v) for k, v in self.tier_a.items()},
            "tier_b": {k: classification_to_dict(v) for k, v in self.tier_b.items()},
            "quarantined": {k: classification_to_dict(v) for k, v in self.quarantined.items()},
            "summary": self.summary(),
        }
    
    def save(self, path: str = ".neurop_verified/tier_registry.json") -> None:
        """Save tier registry to file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: str = ".neurop_verified/tier_registry.json") -> "TierRegistry":
        """Load tier registry from file."""
        p = Path(path)
        if not p.exists():
            return cls()
        try:
            data = json.loads(p.read_text())
            registry = cls()
            for block_id, c in data.get("tier_a", {}).items():
                registry.tier_a[block_id] = TierClassification(
                    block_id=c["block_id"],
                    block_name=c["block_name"],
                    tier=BlockTier.TIER_A,
                    reasons=c["reasons"],
                    confidence=c["confidence"],
                    input_complexity=c["input_complexity"],
                    has_external_deps=c["has_external_deps"],
                    is_pure_function=c["is_pure_function"],
                )
            for block_id, c in data.get("tier_b", {}).items():
                registry.tier_b[block_id] = TierClassification(
                    block_id=c["block_id"],
                    block_name=c["block_name"],
                    tier=BlockTier.TIER_B,
                    reasons=c["reasons"],
                    confidence=c["confidence"],
                    input_complexity=c["input_complexity"],
                    has_external_deps=c["has_external_deps"],
                    is_pure_function=c["is_pure_function"],
                )
            for block_id, c in data.get("quarantined", {}).items():
                registry.quarantined[block_id] = TierClassification(
                    block_id=c["block_id"],
                    block_name=c["block_name"],
                    tier=BlockTier.QUARANTINED,
                    reasons=c["reasons"],
                    confidence=c["confidence"],
                    input_complexity=c["input_complexity"],
                    has_external_deps=c["has_external_deps"],
                    is_pure_function=c["is_pure_function"],
                )
            return registry
        except Exception:
            return cls()


EXTERNAL_DEPS_KEYWORDS = {
    'import ', 'from ', 'requests.', 'urllib.', 'http.', 'socket.',
    'subprocess.', 'os.system', 'open(', 'file.', 'database',
    'sql', 'mongo', 'redis', 'api.', 'fetch', 'async ', 'await ',
}

PURE_FUNCTION_INDICATORS = {
    'return ', 'def ', 'lambda ', 'map(', 'filter(', 'reduce(',
}

CONTEXT_DEPENDENT_KEYWORDS = {
    'datetime.now', 'time.time', 'random.', 'uuid.uuid4',
    'os.environ', 'sys.', 'globals()', 'locals()',
}


class BlockTierClassifier:
    """Classifies blocks into Tier-A or Tier-B."""
    
    def __init__(self, verified_ids: Optional[Set[str]] = None):
        self._verified_ids = verified_ids or set()
        self._registry = TierRegistry.load()
    
    def classify_block(self, block: NeuropBlock) -> TierClassification:
        """Classify a single block into a tier."""
        block_id = block.get_identity_hash() if hasattr(block, 'get_identity_hash') else str(id(block))
        block_name = block.metadata.name if hasattr(block.metadata, 'name') else "unknown"
        
        reasons = []
        confidence = 1.0
        
        if block_id not in self._verified_ids:
            reasons.append("Block not verified")
            return TierClassification(
                block_id=block_id,
                block_name=block_name,
                tier=BlockTier.QUARANTINED,
                reasons=reasons,
                confidence=0.0,
                input_complexity=len(block.interface.inputs),
                has_external_deps=False,
                is_pure_function=False,
            )
        
        logic = block.logic or ""
        logic_lower = logic.lower()
        
        has_external_deps = any(kw.lower() in logic_lower for kw in EXTERNAL_DEPS_KEYWORDS)
        is_context_dependent = any(kw.lower() in logic_lower for kw in CONTEXT_DEPENDENT_KEYWORDS)
        is_pure = any(kw.lower() in logic_lower for kw in PURE_FUNCTION_INDICATORS) and not is_context_dependent
        
        input_complexity = len(block.interface.inputs)
        
        if has_external_deps:
            reasons.append("Has external dependencies")
            confidence -= 0.3
        
        if is_context_dependent:
            reasons.append("Context-dependent (time, random, etc.)")
            confidence -= 0.4
        
        if input_complexity > 3:
            reasons.append(f"High input complexity ({input_complexity} params)")
            confidence -= 0.1
        
        if input_complexity == 0:
            reasons.append("No inputs - may be constant or side-effect")
            confidence -= 0.2
        
        if is_pure and not has_external_deps and not is_context_dependent:
            reasons.append("Pure function detected")
            confidence += 0.1
        
        has_complex_types = any(
            p.data_type in [DataType.DICT, DataType.LIST, DataType.ANY]
            for p in block.interface.inputs
        )
        if has_complex_types:
            reasons.append("Complex input types (dict/list/any)")
            confidence -= 0.1
        
        confidence = max(0.0, min(1.0, confidence))
        
        if confidence >= 0.7 and not has_external_deps and not is_context_dependent and input_complexity <= 3:
            tier = BlockTier.TIER_A
            reasons.insert(0, "Tier-A: Deterministic, safe block")
        else:
            tier = BlockTier.TIER_B
            reasons.insert(0, "Tier-B: Context-dependent or complex block")
        
        return TierClassification(
            block_id=block_id,
            block_name=block_name,
            tier=tier,
            reasons=reasons,
            confidence=confidence,
            input_complexity=input_complexity,
            has_external_deps=has_external_deps,
            is_pure_function=is_pure,
        )
    
    def classify_all(self, blocks: List[NeuropBlock]) -> TierRegistry:
        """Classify all blocks and return a registry."""
        registry = TierRegistry()
        
        for block in blocks:
            classification = self.classify_block(block)
            
            if classification.tier == BlockTier.TIER_A:
                registry.tier_a[classification.block_id] = classification
            elif classification.tier == BlockTier.TIER_B:
                registry.tier_b[classification.block_id] = classification
            elif classification.tier == BlockTier.QUARANTINED:
                registry.quarantined[classification.block_id] = classification
            else:
                registry.unclassified[classification.block_id] = classification
        
        self._registry = registry
        return registry
    
    def get_registry(self) -> TierRegistry:
        """Get the current tier registry."""
        return self._registry
    
    def save_registry(self) -> None:
        """Save the registry to disk."""
        self._registry.save()


_tier_registry: Optional[TierRegistry] = None


def get_tier_registry() -> TierRegistry:
    """Get the global tier registry."""
    global _tier_registry
    if _tier_registry is None:
        _tier_registry = TierRegistry.load()
    return _tier_registry


def classify_blocks(blocks: List[NeuropBlock], verified_ids: Set[str]) -> TierRegistry:
    """Convenience function to classify blocks."""
    classifier = BlockTierClassifier(verified_ids)
    registry = classifier.classify_all(blocks)
    classifier.save_registry()
    return registry


def print_tier_summary(registry: TierRegistry) -> None:
    """Print tier classification summary."""
    summary = registry.summary()
    print()
    print("=" * 50)
    print("BLOCK TIER CLASSIFICATION")
    print("=" * 50)
    print(f"Tier-A (Deterministic): {summary['tier_a']} blocks")
    print(f"Tier-B (Context-Dependent): {summary['tier_b']} blocks")
    print(f"Quarantined: {summary['quarantined']} blocks")
    print(f"Total Classified: {summary['total']} blocks")
    print()
    
    tier_a_pct = (summary['tier_a'] / summary['total'] * 100) if summary['total'] > 0 else 0
    print(f"Tier-A Rate: {tier_a_pct:.1f}%")
    print()
