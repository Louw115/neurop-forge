"""
Execution-Based Trust Tracker for NeuropBlocks.

This module tracks block execution results and updates trust scores dynamically.
The trust layer is enhanced with:
- Execution count tracking
- Success rate calculation
- Failure pattern detection
- Trust decay for unused blocks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class ExecutionOutcome(Enum):
    """Possible outcomes of block execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ExecutionRecord:
    """Record of a single block execution."""
    block_hash: str
    timestamp: str
    outcome: ExecutionOutcome
    duration_ms: float
    inputs_hash: str
    outputs_hash: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None


@dataclass
class BlockExecutionStats:
    """Aggregate execution statistics for a block."""
    block_hash: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    total_duration_ms: float = 0.0
    last_execution: Optional[str] = None
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    failure_patterns: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    @property
    def avg_duration_ms(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.total_duration_ms / self.execution_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_hash": self.block_hash,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "timeout_count": self.timeout_count,
            "success_rate": self.success_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "last_execution": self.last_execution,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "failure_patterns": self.failure_patterns,
        }


class TrustTracker:
    """
    Tracks block execution and updates trust scores.
    
    Trust is earned through successful execution and lost through failures.
    The tracker maintains execution history and calculates trust adjustments.
    """

    def __init__(self, decay_rate: float = 0.01):
        self._stats: Dict[str, BlockExecutionStats] = {}
        self._decay_rate = decay_rate
        self._base_trust = 0.36

    def record_execution(
        self,
        block_hash: str,
        outcome: ExecutionOutcome,
        duration_ms: float,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
    ) -> ExecutionRecord:
        """Record a block execution and update statistics."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        inputs_hash = str(hash(json.dumps(sorted(inputs.keys()))))
        outputs_hash = None
        if outputs:
            try:
                outputs_hash = str(hash(json.dumps(outputs, default=str)))
            except:
                outputs_hash = str(hash(str(outputs)))

        record = ExecutionRecord(
            block_hash=block_hash,
            timestamp=timestamp,
            outcome=outcome,
            duration_ms=duration_ms,
            inputs_hash=inputs_hash,
            outputs_hash=outputs_hash,
            error_message=str(error) if error else None,
            error_type=type(error).__name__ if error else None,
        )

        if block_hash not in self._stats:
            self._stats[block_hash] = BlockExecutionStats(block_hash=block_hash)

        stats = self._stats[block_hash]
        stats.execution_count += 1
        stats.total_duration_ms += duration_ms
        stats.last_execution = timestamp

        if outcome == ExecutionOutcome.SUCCESS:
            stats.success_count += 1
            stats.last_success = timestamp
        elif outcome == ExecutionOutcome.FAILURE or outcome == ExecutionOutcome.ERROR:
            stats.failure_count += 1
            stats.last_failure = timestamp
            if record.error_type and record.error_type not in stats.failure_patterns:
                stats.failure_patterns.append(record.error_type)
        elif outcome == ExecutionOutcome.TIMEOUT:
            stats.timeout_count += 1
            stats.failure_count += 1
            stats.last_failure = timestamp

        return record

    def get_execution_stats(self, block_hash: str) -> Optional[BlockExecutionStats]:
        """Get execution statistics for a block."""
        return self._stats.get(block_hash)

    def calculate_trust_adjustment(self, block_hash: str) -> float:
        """
        Calculate trust score adjustment based on execution history.
        
        Returns a trust delta (can be positive or negative).
        """
        stats = self._stats.get(block_hash)
        if not stats:
            return 0.0

        success_bonus = stats.success_rate * 0.3

        execution_bonus = min(0.1, stats.execution_count * 0.01)

        failure_penalty = 0.0
        if stats.failure_count > 0:
            failure_ratio = stats.failure_count / stats.execution_count
            failure_penalty = failure_ratio * 0.2

        pattern_penalty = len(stats.failure_patterns) * 0.02

        trust_delta = success_bonus + execution_bonus - failure_penalty - pattern_penalty

        return max(-0.5, min(0.5, trust_delta))

    def get_adjusted_trust_score(
        self, block_hash: str, base_trust: float
    ) -> float:
        """Get the trust score adjusted for execution history."""
        adjustment = self.calculate_trust_adjustment(block_hash)
        adjusted = base_trust + adjustment
        return max(0.0, min(1.0, adjusted))

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get execution statistics for all tracked blocks."""
        return {h: s.to_dict() for h, s in self._stats.items()}

    def get_high_trust_blocks(self, min_executions: int = 5, min_success_rate: float = 0.9) -> List[str]:
        """Get block hashes that meet high trust criteria."""
        high_trust = []
        for block_hash, stats in self._stats.items():
            if stats.execution_count >= min_executions and stats.success_rate >= min_success_rate:
                high_trust.append(block_hash)
        return high_trust

    def get_unreliable_blocks(self, min_executions: int = 3, max_success_rate: float = 0.5) -> List[str]:
        """Get block hashes that are unreliable (low success rate)."""
        unreliable = []
        for block_hash, stats in self._stats.items():
            if stats.execution_count >= min_executions and stats.success_rate <= max_success_rate:
                unreliable.append(block_hash)
        return unreliable


_global_tracker: Optional[TrustTracker] = None


def get_trust_tracker() -> TrustTracker:
    """Get the global trust tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = TrustTracker()
    return _global_tracker


def record_block_execution(
    block_hash: str,
    success: bool,
    duration_ms: float,
    inputs: Dict[str, Any],
    outputs: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
) -> None:
    """Convenience function to record a block execution."""
    tracker = get_trust_tracker()
    outcome = ExecutionOutcome.SUCCESS if success else ExecutionOutcome.FAILURE
    if error:
        if "timeout" in str(error).lower():
            outcome = ExecutionOutcome.TIMEOUT
        else:
            outcome = ExecutionOutcome.ERROR
    
    tracker.record_execution(
        block_hash=block_hash,
        outcome=outcome,
        duration_ms=duration_ms,
        inputs=inputs,
        outputs=outputs,
        error=error,
    )
