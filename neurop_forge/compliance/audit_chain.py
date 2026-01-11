"""
Cryptographic Audit Chain
=========================
Append-only audit log where each entry hashes the previous entry,
creating a tamper-proof chain of execution evidence.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class AuditEntry:
    """Single entry in the audit chain."""
    sequence: int
    timestamp: str
    action: str
    block_name: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    success: bool
    execution_time_ms: float
    agent_id: str
    policy_status: str
    previous_hash: str
    entry_hash: str = field(default="")
    
    def __post_init__(self):
        if not self.entry_hash:
            self.entry_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry including previous hash."""
        content = json.dumps({
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "action": self.action,
            "block_name": self.block_name,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
            "agent_id": self.agent_id,
            "policy_status": self.policy_status,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditChain:
    """
    Cryptographic audit chain for AI execution logging.
    
    Each entry contains:
    - What block was called
    - What inputs were provided
    - What outputs were returned
    - Whether the policy allowed it
    - A hash linking to the previous entry (tamper-proof chain)
    """
    
    GENESIS_HASH = "0" * 64
    
    def __init__(self, agent_id: str = "default-agent"):
        self.agent_id = agent_id
        self.entries: List[AuditEntry] = []
        self.violations: List[AuditEntry] = []
        self._start_time = datetime.now(timezone.utc)
    
    @property
    def last_hash(self) -> str:
        """Get the hash of the last entry, or genesis hash if empty."""
        if not self.entries:
            return self.GENESIS_HASH
        return self.entries[-1].entry_hash
    
    def log_execution(
        self,
        block_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool,
        execution_time_ms: float,
        policy_status: str = "ALLOWED"
    ) -> AuditEntry:
        """Log a block execution to the chain."""
        entry = AuditEntry(
            sequence=len(self.entries) + 1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action="EXECUTE",
            block_name=block_name,
            inputs=self._sanitize_for_log(inputs),
            outputs=self._sanitize_for_log(outputs),
            success=success,
            execution_time_ms=execution_time_ms,
            agent_id=self.agent_id,
            policy_status=policy_status,
            previous_hash=self.last_hash
        )
        self.entries.append(entry)
        return entry
    
    def log_violation(
        self,
        block_name: str,
        inputs: Dict[str, Any],
        reason: str
    ) -> AuditEntry:
        """Log a policy violation to the chain."""
        entry = AuditEntry(
            sequence=len(self.entries) + 1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action="VIOLATION",
            block_name=block_name,
            inputs=self._sanitize_for_log(inputs),
            outputs={"violation_reason": reason},
            success=False,
            execution_time_ms=0.0,
            agent_id=self.agent_id,
            policy_status="BLOCKED",
            previous_hash=self.last_hash
        )
        self.entries.append(entry)
        self.violations.append(entry)
        return entry
    
    def _sanitize_for_log(self, data: Any) -> Any:
        """Sanitize data for JSON serialization."""
        if data is None:
            return None
        if isinstance(data, (str, int, float, bool)):
            return data
        if isinstance(data, dict):
            return {k: self._sanitize_for_log(v) for k, v in data.items()}
        if isinstance(data, (list, tuple)):
            return [self._sanitize_for_log(v) for v in data]
        return str(data)
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the entire chain."""
        if not self.entries:
            return True
        
        expected_prev = self.GENESIS_HASH
        for entry in self.entries:
            if entry.previous_hash != expected_prev:
                return False
            recomputed = entry._compute_hash()
            if entry.entry_hash != recomputed:
                return False
            expected_prev = entry.entry_hash
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the audit chain."""
        return {
            "agent_id": self.agent_id,
            "session_start": self._start_time.isoformat(),
            "total_entries": len(self.entries),
            "successful_executions": sum(1 for e in self.entries if e.success and e.action == "EXECUTE"),
            "failed_executions": sum(1 for e in self.entries if not e.success and e.action == "EXECUTE"),
            "violations": len(self.violations),
            "chain_valid": self.verify_chain(),
            "first_hash": self.entries[0].entry_hash if self.entries else None,
            "last_hash": self.last_hash if self.entries else None
        }
    
    def to_json(self) -> str:
        """Export the entire chain as JSON."""
        return json.dumps({
            "metadata": self.get_summary(),
            "entries": [e.to_dict() for e in self.entries]
        }, indent=2)
    
    def save(self, filepath: str) -> None:
        """Save the audit chain to a file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
