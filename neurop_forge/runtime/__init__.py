"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Runtime Execution Layer - Phase 2 of Neurop Block Forge.

This module provides:
- ExecutionContext: Runtime state and data flow management
- GraphExecutor: Deterministic graph execution engine
- ExecutionResult: Full execution trace with timing

The Runtime completes the loop:
Intent -> Compose -> Execute -> Result
"""

from neurop_forge.runtime.context import (
    ExecutionContext,
    ExecutionVariable,
    ContextScope,
)
from neurop_forge.runtime.executor import (
    GraphExecutor,
    NodeExecutionResult,
    BlockExecutor,
)
from neurop_forge.runtime.result import (
    ExecutionResult,
    ExecutionTrace,
    ExecutionStatus,
)
from neurop_forge.runtime.guards import (
    ExecutionGuard,
    RetryPolicy,
    CircuitBreaker,
)
from neurop_forge.runtime.adapter import (
    FunctionAdapter,
    FunctionSignature,
    SemanticInputMapper,
)
from neurop_forge.runtime.reference_workflows import (
    ReferenceWorkflowRunner,
    run_reference_workflows,
    print_reference_workflow_results,
    REFERENCE_WORKFLOWS,
)

__all__ = [
    "ExecutionContext",
    "ExecutionVariable",
    "ContextScope",
    "GraphExecutor",
    "NodeExecutionResult",
    "BlockExecutor",
    "ExecutionResult",
    "ExecutionTrace",
    "ExecutionStatus",
    "ExecutionGuard",
    "RetryPolicy",
    "CircuitBreaker",
    "FunctionAdapter",
    "FunctionSignature",
    "SemanticInputMapper",
    "ReferenceWorkflowRunner",
    "run_reference_workflows",
    "print_reference_workflow_results",
    "REFERENCE_WORKFLOWS",
]
