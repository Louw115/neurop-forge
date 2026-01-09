"""
Immutable block storage for NeuropBlocks.

This module provides persistent, immutable storage for validated blocks.
Once stored, blocks cannot be modified - only new versions can be created.
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

from neurop_forge.core.block_schema import NeuropBlock


class StoreStatus(Enum):
    """Status of storage operation."""
    STORED = "stored"
    ALREADY_EXISTS = "already_exists"
    VALIDATION_FAILED = "validation_failed"
    STORAGE_ERROR = "storage_error"


@dataclass
class StoreResult:
    """Result of a storage operation."""
    status: StoreStatus
    block_identity: str
    storage_path: Optional[str]
    timestamp: str
    error_message: Optional[str]

    def is_success(self) -> bool:
        return self.status in (StoreStatus.STORED, StoreStatus.ALREADY_EXISTS)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "block_identity": self.block_identity,
            "storage_path": self.storage_path,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
        }


class BlockStore:
    """
    Immutable storage for validated NeuropBlocks.
    
    Features:
    - Content-addressable storage (identity = hash)
    - Immutability enforcement
    - Integrity verification
    - Quarantine support for invalid blocks
    """

    def __init__(
        self,
        storage_path: str = ".neurop_library",
        quarantine_path: str = ".neurop_quarantine",
    ):
        self._storage_path = Path(storage_path)
        self._quarantine_path = Path(quarantine_path)
        self._blocks: Dict[str, NeuropBlock] = {}
        self._quarantine: Dict[str, NeuropBlock] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._quarantine_path.mkdir(parents=True, exist_ok=True)

        self._load_existing_blocks()

    def _load_existing_blocks(self) -> None:
        """Load existing blocks from storage."""
        for block_file in self._storage_path.glob("*.json"):
            try:
                content = block_file.read_text()
                data = json.loads(content)
                block = NeuropBlock.from_dict(data)
                identity = block.get_identity_hash()
                self._blocks[identity] = block
            except Exception:
                pass

        for block_file in self._quarantine_path.glob("*.json"):
            try:
                content = block_file.read_text()
                data = json.loads(content)
                block = NeuropBlock.from_dict(data)
                identity = block.get_identity_hash()
                self._quarantine[identity] = block
            except Exception:
                pass

    def store(self, block: NeuropBlock) -> StoreResult:
        """
        Store a validated block.
        
        Args:
            block: The block to store
            
        Returns:
            StoreResult with operation status
        """
        identity = block.get_identity_hash()
        timestamp = datetime.now(timezone.utc).isoformat()

        if identity in self._blocks:
            return StoreResult(
                status=StoreStatus.ALREADY_EXISTS,
                block_identity=identity,
                storage_path=str(self._get_block_path(identity)),
                timestamp=timestamp,
                error_message=None,
            )

        if not self._verify_integrity(block):
            return StoreResult(
                status=StoreStatus.VALIDATION_FAILED,
                block_identity=identity,
                storage_path=None,
                timestamp=timestamp,
                error_message="Block integrity verification failed",
            )

        try:
            block_path = self._get_block_path(identity)
            block_json = block.to_json()
            block_path.write_text(block_json)

            self._blocks[identity] = block
            self._metadata[identity] = {
                "stored_at": timestamp,
                "file_path": str(block_path),
                "file_size": len(block_json),
            }

            return StoreResult(
                status=StoreStatus.STORED,
                block_identity=identity,
                storage_path=str(block_path),
                timestamp=timestamp,
                error_message=None,
            )

        except Exception as e:
            return StoreResult(
                status=StoreStatus.STORAGE_ERROR,
                block_identity=identity,
                storage_path=None,
                timestamp=timestamp,
                error_message=str(e),
            )

    def quarantine(self, block: NeuropBlock, reason: str) -> StoreResult:
        """
        Quarantine an invalid block.
        
        Quarantined blocks are never exposed to AI assembly.
        
        Args:
            block: The block to quarantine
            reason: Reason for quarantine
            
        Returns:
            StoreResult with operation status
        """
        identity = block.get_identity_hash()
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            quarantine_path = self._quarantine_path / f"{identity[:16]}.json"

            block_data = block.to_dict()
            block_data["quarantine_reason"] = reason
            block_data["quarantine_timestamp"] = timestamp

            quarantine_path.write_text(json.dumps(block_data, indent=2))

            self._quarantine[identity] = block

            return StoreResult(
                status=StoreStatus.STORED,
                block_identity=identity,
                storage_path=str(quarantine_path),
                timestamp=timestamp,
                error_message=None,
            )

        except Exception as e:
            return StoreResult(
                status=StoreStatus.STORAGE_ERROR,
                block_identity=identity,
                storage_path=None,
                timestamp=timestamp,
                error_message=str(e),
            )

    def get(self, identity: str) -> Optional[NeuropBlock]:
        """
        Retrieve a block by identity.
        
        Args:
            identity: The block identity hash
            
        Returns:
            NeuropBlock if found, None otherwise
        """
        return self._blocks.get(identity)

    def get_all(self) -> List[NeuropBlock]:
        """Get all stored blocks."""
        return list(self._blocks.values())

    def get_by_category(self, category: str) -> List[NeuropBlock]:
        """Get blocks by category."""
        return [
            block for block in self._blocks.values()
            if block.metadata.category == category
        ]

    def get_by_intent(self, intent_keywords: List[str]) -> List[NeuropBlock]:
        """Get blocks matching intent keywords."""
        matching = []
        for block in self._blocks.values():
            intent = block.metadata.intent.lower()
            name = block.metadata.name.lower()
            tags = [t.lower() for t in block.metadata.tags]

            for keyword in intent_keywords:
                kw = keyword.lower()
                if kw in intent or kw in name or kw in tags:
                    matching.append(block)
                    break

        return matching

    def exists(self, identity: str) -> bool:
        """Check if a block exists."""
        return identity in self._blocks

    def is_quarantined(self, identity: str) -> bool:
        """Check if a block is quarantined."""
        return identity in self._quarantine

    def count(self) -> int:
        """Get total number of stored blocks."""
        return len(self._blocks)

    def _get_block_path(self, identity: str) -> Path:
        """Get the file path for a block."""
        short_id = identity[:16]
        return self._storage_path / f"{short_id}.json"

    def _verify_integrity(self, block: NeuropBlock) -> bool:
        """Verify block integrity."""
        try:
            if not block.identity:
                return False
            if not block.logic:
                return False
            if block.trust_score.overall_score <= 0:
                return False
            return True
        except Exception:
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        categories: Dict[str, int] = {}
        languages: Dict[str, int] = {}
        total_trust = 0.0

        for block in self._blocks.values():
            cat = block.metadata.category
            categories[cat] = categories.get(cat, 0) + 1

            lang = block.metadata.language
            languages[lang] = languages.get(lang, 0) + 1

            total_trust += block.trust_score.overall_score

        return {
            "total_blocks": len(self._blocks),
            "quarantined_blocks": len(self._quarantine),
            "categories": categories,
            "languages": languages,
            "average_trust": total_trust / max(len(self._blocks), 1),
        }
