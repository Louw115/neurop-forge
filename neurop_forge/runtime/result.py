"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

ExecutionResult - Complete execution results with trace and timing.

Provides full visibility into:
- What executed and in what order
- How long each step took
- What data flowed between blocks
- Any errors that occurred
- Final outputs
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import json


class ExecutionStatus(Enum):
    """Execution status codes."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class ExecutionTrace:
    """Trace of a single block execution."""
    node_id: str
    block_name: str
    status: ExecutionStatus
    started_at: str
    completed_at: str
    duration_ms: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    error: Optional[str] = None
    retry_count: int = 0
    skipped_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "block_name": self.block_name,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "inputs": self._safe_serialize(self.inputs),
            "outputs": self._safe_serialize(self.outputs),
            "error": self.error,
            "retry_count": self.retry_count,
            "skipped_reason": self.skipped_reason,
        }
    
    def _safe_serialize(self, data: Any) -> Any:
        """Safely serialize data for output."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, (list, tuple)):
            return [self._safe_serialize(v) for v in data]
        if isinstance(data, dict):
            return {str(k): self._safe_serialize(v) for k, v in data.items()}
        return str(data)


@dataclass
class ExecutionResult:
    """
    Complete result of graph execution.
    
    Contains:
    - Final status and outputs
    - Full execution trace
    - Timing information
    - Error details if any
    - Performance metrics
    """
    execution_id: str
    query: str
    status: ExecutionStatus
    started_at: str
    completed_at: str
    total_duration_ms: float
    traces: List[ExecutionTrace]
    final_outputs: Dict[str, Any]
    error: Optional[str] = None
    nodes_executed: int = 0
    nodes_succeeded: int = 0
    nodes_failed: int = 0
    nodes_skipped: int = 0
    
    def __post_init__(self):
        if not self.nodes_executed:
            self.nodes_executed = len(self.traces)
            self.nodes_succeeded = sum(
                1 for t in self.traces if t.status == ExecutionStatus.SUCCESS
            )
            self.nodes_failed = sum(
                1 for t in self.traces if t.status == ExecutionStatus.FAILED
            )
            self.nodes_skipped = sum(
                1 for t in self.traces if t.status == ExecutionStatus.SKIPPED
            )
    
    @property
    def is_success(self) -> bool:
        """Check if execution was fully successful."""
        return self.status == ExecutionStatus.SUCCESS
    
    @property
    def is_partial(self) -> bool:
        """Check if execution was partially successful."""
        return self.status == ExecutionStatus.PARTIAL_SUCCESS
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.nodes_executed == 0:
            return 0.0
        return self.nodes_succeeded / self.nodes_executed
    
    def get_trace(self, node_id: str) -> Optional[ExecutionTrace]:
        """Get trace for a specific node."""
        for trace in self.traces:
            if trace.node_id == node_id:
                return trace
        return None
    
    def get_output(self, key: str, default: Any = None) -> Any:
        """Get a specific output value."""
        return self.final_outputs.get(key, default)
    
    def get_first_error(self) -> Optional[str]:
        """Get the first error that occurred."""
        for trace in self.traces:
            if trace.error:
                return f"{trace.block_name}: {trace.error}"
        return self.error
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.traces:
            return {"total_ms": self.total_duration_ms, "nodes": 0}
        
        durations = [t.duration_ms for t in self.traces]
        return {
            "total_ms": self.total_duration_ms,
            "nodes": len(self.traces),
            "avg_node_ms": sum(durations) / len(durations),
            "max_node_ms": max(durations),
            "min_node_ms": min(durations),
            "slowest_node": max(self.traces, key=lambda t: t.duration_ms).block_name,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "execution_id": self.execution_id,
            "query": self.query,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_ms": self.total_duration_ms,
            "nodes_executed": self.nodes_executed,
            "nodes_succeeded": self.nodes_succeeded,
            "nodes_failed": self.nodes_failed,
            "nodes_skipped": self.nodes_skipped,
            "success_rate": self.success_rate,
            "error": self.error,
            "traces": [t.to_dict() for t in self.traces],
            "final_outputs": self._safe_serialize(self.final_outputs),
            "performance": self.get_performance_summary(),
        }
    
    def _safe_serialize(self, data: Any) -> Any:
        """Safely serialize data."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, (list, tuple)):
            return [self._safe_serialize(v) for v in data]
        if isinstance(data, dict):
            return {str(k): self._safe_serialize(v) for k, v in data.items()}
        return str(data)
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def print_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Execution: {self.execution_id}",
            f"Query: {self.query}",
            f"Status: {self.status.value.upper()}",
            f"Duration: {self.total_duration_ms:.2f}ms",
            f"Nodes: {self.nodes_succeeded}/{self.nodes_executed} succeeded",
        ]
        
        if self.error:
            lines.append(f"Error: {self.error}")
        
        lines.append("\nExecution Trace:")
        for trace in self.traces:
            status_icon = "✓" if trace.status == ExecutionStatus.SUCCESS else "✗"
            lines.append(f"  {status_icon} {trace.block_name} ({trace.duration_ms:.2f}ms)")
            if trace.error:
                lines.append(f"    Error: {trace.error}")
        
        if self.final_outputs:
            lines.append("\nFinal Outputs:")
            for key, value in self.final_outputs.items():
                val_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                lines.append(f"  {key}: {val_str}")
        
        return "\n".join(lines)
