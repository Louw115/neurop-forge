"""
Block Deduplication Engine for Neurop Forge V2.

Detects and resolves duplicate block names with different signatures.
"""

from neurop_forge.deduplication.signature_hasher import SignatureHasher
from neurop_forge.deduplication.policy_engine import DeduplicationPolicy, PolicyEngine
from neurop_forge.deduplication.dedup_processor import DeduplicationProcessor
from neurop_forge.deduplication.dedup_report import DeduplicationReport

__all__ = [
    "SignatureHasher",
    "DeduplicationPolicy", 
    "PolicyEngine",
    "DeduplicationProcessor",
    "DeduplicationReport",
]
