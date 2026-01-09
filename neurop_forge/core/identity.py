"""
Canonical hash and identity authority for NeuropBlocks.

This module provides deterministic, reproducible identity generation
based on the semantic content of blocks. Identity is derived from:
- Normalized logic representation
- Interface specification
- Constraints declaration

The identity is immutable once created and serves as the canonical
reference for the block across all operations.
"""

import hashlib
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class HashAlgorithm(Enum):
    """Supported hash algorithms for identity generation."""
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


@dataclass(frozen=True)
class BlockIdentity:
    """
    Immutable identity for a NeuropBlock.
    
    Attributes:
        hash_value: The canonical hash of the block content
        algorithm: The hash algorithm used
        version: Schema version for forward compatibility
        semantic_fingerprint: Hash of normalized semantic content
    """
    hash_value: str
    algorithm: HashAlgorithm
    version: str
    semantic_fingerprint: str

    def __str__(self) -> str:
        return f"neurop:{self.algorithm.value}:{self.hash_value[:16]}"

    def full_id(self) -> str:
        return f"neurop:{self.algorithm.value}:{self.hash_value}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash_value": self.hash_value,
            "algorithm": self.algorithm.value,
            "version": self.version,
            "semantic_fingerprint": self.semantic_fingerprint,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockIdentity":
        return cls(
            hash_value=data["hash_value"],
            algorithm=HashAlgorithm(data["algorithm"]),
            version=data["version"],
            semantic_fingerprint=data["semantic_fingerprint"],
        )


class IdentityAuthority:
    """
    The canonical authority for generating and verifying NeuropBlock identities.
    
    This class ensures that:
    - All identities are deterministically derived from content
    - The same semantic content always produces the same identity
    - Identities are reproducible across system restarts
    - Hash collisions are detected and rejected
    """

    SCHEMA_VERSION = "1.0.0"
    DEFAULT_ALGORITHM = HashAlgorithm.SHA256

    def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
        self._algorithm = algorithm
        self._known_identities: Dict[str, Dict[str, Any]] = {}

    def _get_hasher(self) -> Any:
        """Get the appropriate hasher for the configured algorithm."""
        if self._algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256()
        elif self._algorithm == HashAlgorithm.SHA384:
            return hashlib.sha384()
        elif self._algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512()
        else:
            raise ValueError(f"Unsupported algorithm: {self._algorithm}")

    def _canonicalize(self, data: Dict[str, Any]) -> str:
        """
        Convert data to canonical JSON representation for hashing.
        
        This ensures the same logical content always produces the same string,
        regardless of key ordering or whitespace.
        """
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def _compute_hash(self, content: str) -> str:
        """Compute hash of the given content string."""
        hasher = self._get_hasher()
        hasher.update(content.encode("utf-8"))
        return hasher.hexdigest()

    def generate_identity(
        self,
        normalized_logic: str,
        interface: Dict[str, Any],
        constraints: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BlockIdentity:
        """
        Generate a canonical identity for a NeuropBlock.
        
        Args:
            normalized_logic: The normalized code/logic representation
            interface: The typed input/output specification
            constraints: Runtime, purity, and I/O constraints
            metadata: Optional metadata (not included in semantic hash)
            
        Returns:
            BlockIdentity: The immutable identity for this block
            
        Raises:
            ValueError: If inputs are invalid or would cause collision
        """
        if not normalized_logic or not normalized_logic.strip():
            raise ValueError("Normalized logic cannot be empty")

        if not interface:
            raise ValueError("Interface specification is required")

        if not constraints:
            raise ValueError("Constraints specification is required")

        semantic_content = {
            "logic": normalized_logic,
            "interface": interface,
            "constraints": constraints,
        }

        canonical_string = self._canonicalize(semantic_content)
        semantic_fingerprint = self._compute_hash(canonical_string)

        full_content = {
            "semantic": semantic_content,
            "version": self.SCHEMA_VERSION,
            "algorithm": self._algorithm.value,
        }

        full_canonical = self._canonicalize(full_content)
        full_hash = self._compute_hash(full_canonical)

        if full_hash in self._known_identities:
            existing = self._known_identities[full_hash]
            if existing["semantic_fingerprint"] != semantic_fingerprint:
                raise ValueError(
                    f"Hash collision detected for {full_hash}. "
                    "Different semantic content produces same hash."
                )

        identity = BlockIdentity(
            hash_value=full_hash,
            algorithm=self._algorithm,
            version=self.SCHEMA_VERSION,
            semantic_fingerprint=semantic_fingerprint,
        )

        self._known_identities[full_hash] = {
            "semantic_fingerprint": semantic_fingerprint,
            "canonical_content": full_canonical,
        }

        return identity

    def verify_identity(
        self,
        identity: BlockIdentity,
        normalized_logic: str,
        interface: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> bool:
        """
        Verify that a block's content matches its claimed identity.
        
        Args:
            identity: The claimed identity
            normalized_logic: The block's normalized logic
            interface: The block's interface specification
            constraints: The block's constraints
            
        Returns:
            bool: True if the identity matches the content
        """
        try:
            computed = self.generate_identity(normalized_logic, interface, constraints)
            return (
                computed.hash_value == identity.hash_value
                and computed.semantic_fingerprint == identity.semantic_fingerprint
            )
        except ValueError:
            return False

    def regenerate_identity(
        self,
        normalized_logic: str,
        interface: Dict[str, Any],
        constraints: Dict[str, Any],
    ) -> BlockIdentity:
        """
        Regenerate identity for verification purposes.
        
        This is used to verify that a block's identity is reproducible.
        """
        return self.generate_identity(normalized_logic, interface, constraints)

    def get_algorithm(self) -> HashAlgorithm:
        """Get the current hash algorithm."""
        return self._algorithm

    def clear_cache(self) -> None:
        """Clear the known identities cache. Use with caution."""
        self._known_identities.clear()
