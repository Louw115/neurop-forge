"""
Block Verification System

Automatically tests all blocks and marks them as verified or quarantined.
Only verified blocks are used in semantic composition.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

from neurop_forge.core.block_schema import NeuropBlock, DataType
from neurop_forge.runtime.executor import BlockExecutor


@dataclass
class VerificationResult:
    """Result of verifying a single block."""
    block_id: str
    block_name: str
    verified: bool
    test_input: Dict[str, Any]
    test_output: Optional[Dict[str, Any]]
    error: Optional[str]
    duration_ms: float
    timestamp: str


@dataclass 
class VerificationRegistry:
    """Tracks verification status for all blocks."""
    verified_blocks: Dict[str, VerificationResult] = field(default_factory=dict)
    failed_blocks: Dict[str, VerificationResult] = field(default_factory=dict)
    last_run: Optional[str] = None
    
    def is_verified(self, block_id: str) -> bool:
        return block_id in self.verified_blocks
    
    def get_verified_ids(self) -> List[str]:
        return list(self.verified_blocks.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified_blocks": {k: self._result_to_dict(v) for k, v in self.verified_blocks.items()},
            "failed_blocks": {k: self._result_to_dict(v) for k, v in self.failed_blocks.items()},
            "last_run": self.last_run,
            "summary": {
                "total_verified": len(self.verified_blocks),
                "total_failed": len(self.failed_blocks),
            }
        }
    
    def _result_to_dict(self, r: VerificationResult) -> Dict[str, Any]:
        return {
            "block_id": r.block_id,
            "block_name": r.block_name,
            "verified": r.verified,
            "error": r.error,
            "duration_ms": r.duration_ms,
            "timestamp": r.timestamp,
        }
    
    def save(self, path: str = ".neurop_verified/registry.json") -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: str = ".neurop_verified/registry.json") -> "VerificationRegistry":
        p = Path(path)
        if not p.exists():
            return cls()
        try:
            data = json.loads(p.read_text())
            registry = cls()
            registry.last_run = data.get("last_run")
            for block_id, r in data.get("verified_blocks", {}).items():
                registry.verified_blocks[block_id] = VerificationResult(
                    block_id=r["block_id"],
                    block_name=r["block_name"],
                    verified=r["verified"],
                    test_input={},
                    test_output=None,
                    error=r.get("error"),
                    duration_ms=r["duration_ms"],
                    timestamp=r["timestamp"],
                )
            for block_id, r in data.get("failed_blocks", {}).items():
                registry.failed_blocks[block_id] = VerificationResult(
                    block_id=r["block_id"],
                    block_name=r["block_name"],
                    verified=r["verified"],
                    test_input={},
                    test_output=None,
                    error=r.get("error"),
                    duration_ms=r["duration_ms"],
                    timestamp=r["timestamp"],
                )
            return registry
        except Exception:
            return cls()


_registry: Optional[VerificationRegistry] = None


def get_verification_registry() -> VerificationRegistry:
    global _registry
    if _registry is None:
        _registry = VerificationRegistry.load()
    return _registry


def generate_test_input(block: NeuropBlock) -> Dict[str, Any]:
    """Generate minimal valid test inputs based on parameter types."""
    inputs = {}
    
    type_defaults = {
        DataType.STRING: "test",
        DataType.INTEGER: 42,
        DataType.FLOAT: 3.14,
        DataType.BOOLEAN: True,
        DataType.LIST: [1, 2, 3],
        DataType.DICT: {"key": "value"},
        DataType.ANY: "test",
        DataType.NONE: None,
        DataType.BYTES: b"test",
    }
    
    name_hints = {
        "text": "hello world",
        "s": "hello world",
        "string": "hello world",
        "value": "test value",
        "n": 42,
        "number": 42,
        "num": 42,
        "x": 10,
        "y": 20,
        "a": 5,
        "b": 3,
        "items": [1, 2, 3],
        "lst": [1, 2, 3],
        "data": {"key": "value"},
        "obj": {"key": "value"},
        "flag": True,
        "enabled": True,
    }
    
    for param in block.interface.inputs:
        name = param.name.lower()
        
        if name in name_hints:
            inputs[param.name] = name_hints[name]
        elif param.data_type in type_defaults:
            inputs[param.name] = type_defaults[param.data_type]
        else:
            inputs[param.name] = "test"
    
    return inputs


class BlockVerifier:
    """Verifies blocks by executing them with test inputs."""
    
    def __init__(self):
        self._executor = BlockExecutor()
        self._registry = get_verification_registry()
    
    def verify_block(self, block: NeuropBlock) -> VerificationResult:
        """Verify a single block."""
        block_id = block.get_identity_hash() if hasattr(block, 'get_identity_hash') else (block.identity.get("hash_value", "") if isinstance(block.identity, dict) else str(id(block)))
        block_name = block.metadata.name if hasattr(block.metadata, 'name') else "unknown"
        
        test_input = generate_test_input(block)
        
        start = time.time()
        try:
            outputs, error = self._executor.execute(block, test_input)
            duration_ms = (time.time() - start) * 1000
            
            verified = error is None and outputs is not None
            
            result = VerificationResult(
                block_id=block_id,
                block_name=block_name,
                verified=verified,
                test_input=test_input,
                test_output=outputs if verified else None,
                error=error,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            
            if verified:
                self._registry.verified_blocks[block_id] = result
            else:
                self._registry.failed_blocks[block_id] = result
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            result = VerificationResult(
                block_id=block_id,
                block_name=block_name,
                verified=False,
                test_input=test_input,
                test_output=None,
                error=f"{type(e).__name__}: {str(e)}",
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            self._registry.failed_blocks[block_id] = result
            return result
    
    def verify_all(self, blocks: List[NeuropBlock], progress_callback=None) -> Dict[str, Any]:
        """Verify all blocks in the library."""
        total = len(blocks)
        verified_count = 0
        failed_count = 0
        
        for i, block in enumerate(blocks):
            result = self.verify_block(block)
            
            if result.verified:
                verified_count += 1
            else:
                failed_count += 1
            
            if progress_callback and (i + 1) % 100 == 0:
                progress_callback(i + 1, total, verified_count, failed_count)
        
        self._registry.last_run = datetime.now(timezone.utc).isoformat()
        self._registry.save()
        
        return {
            "total": total,
            "verified": verified_count,
            "failed": failed_count,
            "success_rate": verified_count / total if total > 0 else 0,
        }
    
    def get_registry(self) -> VerificationRegistry:
        return self._registry


def run_verification(block_store) -> Dict[str, Any]:
    """Run verification on all blocks in the store."""
    verifier = BlockVerifier()
    blocks = list(block_store.get_all())
    
    print(f"Verifying {len(blocks)} blocks...")
    
    def progress(current, total, verified, failed):
        print(f"  Progress: {current}/{total} ({verified} verified, {failed} failed)")
    
    result = verifier.verify_all(blocks, progress_callback=progress)
    
    print(f"\nVerification Complete:")
    print(f"  Total: {result['total']}")
    print(f"  Verified: {result['verified']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Success Rate: {result['success_rate']*100:.1f}%")
    
    return result
