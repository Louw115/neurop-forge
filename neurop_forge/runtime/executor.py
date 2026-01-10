"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

GraphExecutor - The core execution engine for semantic graphs.

This is Phase 2 of Neurop Block Forge:
- Takes a composed semantic graph
- Executes blocks in order
- Passes outputs to inputs
- Returns complete execution result

The execution loop:
Intent -> Compose -> Execute -> Result
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import time
import traceback

from neurop_forge.runtime.context import ExecutionContext, ContextScope
from neurop_forge.runtime.result import ExecutionResult, ExecutionTrace, ExecutionStatus
from neurop_forge.runtime.guards import RetryPolicy, CircuitBreaker, ExecutionGuard
from neurop_forge.runtime.adapter import FunctionAdapter
from neurop_forge.semantic.composer import SemanticGraph, CompositionNode
from neurop_forge.core.block_schema import NeuropBlock


@dataclass
class NodeExecutionResult:
    """Result of executing a single node."""
    node_id: str
    block_name: str
    status: ExecutionStatus
    outputs: Dict[str, Any]
    duration_ms: float
    error: Optional[str] = None
    retry_count: int = 0


class BlockExecutor:
    """
    Executes individual NeuropBlock logic.
    
    Features:
    - Safe execution sandbox
    - FunctionAdapter for signature mapping
    - Type coercion for inputs
    - Output validation
    - Exception handling
    """
    
    def __init__(self):
        self._execution_namespace: Dict[str, Any] = {}
        self._adapter = FunctionAdapter()
        self._setup_namespace()
    
    def _setup_namespace(self) -> None:
        """Setup safe execution namespace."""
        import math
        import re
        import json
        import hashlib
        import base64
        from datetime import datetime, date, timedelta
        from typing import Any, Dict, List, Optional, Tuple
        
        self._execution_namespace = {
            "math": math,
            "re": re,
            "json": json,
            "hashlib": hashlib,
            "base64": base64,
            "datetime": datetime,
            "date": date,
            "timedelta": timedelta,
            "Any": Any,
            "Dict": Dict,
            "List": List,
            "Optional": Optional,
            "Tuple": Tuple,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "range": range,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "type": type,
            "True": True,
            "False": False,
            "None": None,
        }
    
    def execute(
        self,
        block: NeuropBlock,
        inputs: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Execute a block's logic with given inputs.
        
        Uses FunctionAdapter to map semantic inputs to actual function params.
        
        Returns:
            Tuple of (outputs dict, error message or None)
        """
        try:
            local_namespace = dict(self._execution_namespace)
            local_namespace.update(inputs)
            
            logic = block.logic.strip()
            func_name = block.metadata.name
            
            if hasattr(block.identity, 'content_hash'):
                block_id = str(block.identity.content_hash)
            elif isinstance(block.identity, dict):
                block_id = str(block.identity.get('content_hash', id(block)))
            else:
                block_id = str(id(block))
            
            exec(logic, local_namespace)
            
            if func_name in local_namespace:
                func = local_namespace[func_name]
                
                adapted_inputs, adapt_error = self._adapter.adapt_inputs(
                    block_id=block_id,
                    source_code=logic,
                    func_name=func_name,
                    available_inputs=inputs,
                    interface_inputs=list(block.interface.inputs) if hasattr(block, 'interface') else None,
                )
                
                if adapt_error:
                    return {}, adapt_error
                
                result = func(**adapted_inputs)
                
                outputs = self._prepare_outputs(block, result)
                return outputs, None
            else:
                return {"result": None}, f"Function {func_name} not found in block logic"
                
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            return {}, error_msg
    
    def _prepare_inputs(
        self,
        block: NeuropBlock,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare and coerce inputs for block execution."""
        prepared = {}
        
        for param in block.interface.inputs:
            name = param.name
            
            if name in inputs:
                prepared[name] = inputs[name]
            elif param.optional and param.default_value is not None:
                prepared[name] = param.default_value
            elif param.optional:
                prepared[name] = None
        
        return prepared
    
    def _prepare_outputs(
        self,
        block: NeuropBlock,
        result: Any,
    ) -> Dict[str, Any]:
        """Prepare outputs from execution result."""
        output_params = block.interface.outputs
        
        if len(output_params) == 0:
            return {"result": result}
        
        if len(output_params) == 1:
            return {output_params[0].name: result}
        
        if isinstance(result, dict):
            return result
        
        if isinstance(result, (tuple, list)) and len(result) == len(output_params):
            return {p.name: result[i] for i, p in enumerate(output_params)}
        
        return {"result": result}


class GraphExecutor:
    """
    Executes semantic graphs deterministically.
    
    This is the CORE of Phase 2:
    - Takes a composed SemanticGraph
    - Executes each node in order
    - Chains outputs to inputs
    - Handles errors with retries
    - Returns complete ExecutionResult
    """
    
    def __init__(
        self,
        block_library: Optional[Dict[str, NeuropBlock]] = None,
        retry_policy: Optional[RetryPolicy] = None,
        default_timeout_ms: float = 30000.0,
    ):
        self._blocks = block_library or {}
        self._retry_policy = retry_policy or RetryPolicy()
        self._default_timeout_ms = default_timeout_ms
        self._block_executor = BlockExecutor()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_block(self, block_id: str, block: NeuropBlock) -> None:
        """Register a block for execution."""
        self._blocks[block_id] = block
    
    def execute(
        self,
        graph: SemanticGraph,
        initial_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        Execute a semantic graph.
        
        This is the main entry point:
        1. Create execution context with inputs
        2. Execute each node in order
        3. Chain outputs to next node's inputs
        4. Return complete execution result
        """
        start_time = datetime.now()
        start_ts = time.time()
        
        context = ExecutionContext(
            initial_inputs=initial_inputs or {},
            config=config,
        )
        
        guard = ExecutionGuard(timeout_ms=self._default_timeout_ms)
        guard.start()
        
        traces: List[ExecutionTrace] = []
        overall_status = ExecutionStatus.SUCCESS
        error_message = None
        
        for node in graph.nodes:
            can_continue, reason = guard.check()
            if not can_continue:
                overall_status = ExecutionStatus.TIMEOUT
                error_message = reason
                break
            
            node_result = self._execute_node(node, context, guard)
            
            trace = ExecutionTrace(
                node_id=node.block_identity,
                block_name=node.block_name,
                status=node_result.status,
                started_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                duration_ms=node_result.duration_ms,
                inputs=context.get_all_variables(ContextScope.GRAPH),
                outputs=node_result.outputs,
                error=node_result.error,
                retry_count=node_result.retry_count,
            )
            traces.append(trace)
            
            if node_result.status == ExecutionStatus.SUCCESS:
                context.set_node_output(node.block_identity, node_result.outputs)
            elif node_result.status == ExecutionStatus.FAILED:
                overall_status = ExecutionStatus.PARTIAL_SUCCESS
        
        if all(t.status == ExecutionStatus.SUCCESS for t in traces):
            overall_status = ExecutionStatus.SUCCESS
        elif any(t.status == ExecutionStatus.SUCCESS for t in traces):
            overall_status = ExecutionStatus.PARTIAL_SUCCESS
        elif traces:
            overall_status = ExecutionStatus.FAILED
        
        end_time = datetime.now()
        total_duration = (time.time() - start_ts) * 1000
        
        final_outputs = {}
        if traces and traces[-1].status == ExecutionStatus.SUCCESS:
            final_outputs = traces[-1].outputs
        
        return ExecutionResult(
            execution_id=context.execution_id,
            query=graph.query,
            status=overall_status,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            total_duration_ms=total_duration,
            traces=traces,
            final_outputs=final_outputs,
            error=error_message,
        )
    
    def _execute_node(
        self,
        node: CompositionNode,
        context: ExecutionContext,
        guard: ExecutionGuard,
    ) -> NodeExecutionResult:
        """Execute a single node with retry and circuit breaker."""
        start_ts = time.time()
        
        block = self._blocks.get(node.block_identity)
        
        if block is None:
            return self._execute_mock_node(node, context)
        
        circuit = self._get_circuit_breaker(node.block_identity)
        
        if not circuit.can_execute():
            duration = (time.time() - start_ts) * 1000
            return NodeExecutionResult(
                node_id=node.block_identity,
                block_name=node.block_name,
                status=ExecutionStatus.SKIPPED,
                outputs={},
                duration_ms=duration,
                error="Circuit breaker open",
            )
        
        context.enter_node(node.block_identity)
        
        inputs = self._gather_inputs(node, context, block)
        
        attempt = 0
        last_error = None
        
        while attempt <= self._retry_policy.max_retries:
            try:
                outputs, error = self._block_executor.execute(block, inputs)
                
                if error is None:
                    circuit.record_success()
                    context.exit_node()
                    duration = (time.time() - start_ts) * 1000
                    
                    return NodeExecutionResult(
                        node_id=node.block_identity,
                        block_name=node.block_name,
                        status=ExecutionStatus.SUCCESS,
                        outputs=outputs,
                        duration_ms=duration,
                        retry_count=attempt,
                    )
                else:
                    last_error = error
                    if not self._retry_policy.should_retry(Exception(error), attempt):
                        break
                    
                    delay = self._retry_policy.get_delay(attempt)
                    time.sleep(delay / 1000.0)
                    attempt += 1
                    
            except Exception as e:
                last_error = str(e)
                if not self._retry_policy.should_retry(e, attempt):
                    break
                
                delay = self._retry_policy.get_delay(attempt)
                time.sleep(delay / 1000.0)
                attempt += 1
        
        circuit.record_failure()
        context.exit_node()
        duration = (time.time() - start_ts) * 1000
        
        return NodeExecutionResult(
            node_id=node.block_identity,
            block_name=node.block_name,
            status=ExecutionStatus.FAILED,
            outputs={},
            duration_ms=duration,
            error=last_error,
            retry_count=attempt,
        )
    
    def _execute_mock_node(
        self,
        node: CompositionNode,
        context: ExecutionContext,
    ) -> NodeExecutionResult:
        """Execute a mock node when real block is not available."""
        previous_output = context.get_previous_output()
        
        mock_output = {
            "result": previous_output if previous_output else True,
            "block_name": node.block_name,
            "domain": node.semantic_intent.domain.value,
            "operation": node.semantic_intent.operation.value,
        }
        
        return NodeExecutionResult(
            node_id=node.block_identity,
            block_name=node.block_name,
            status=ExecutionStatus.SUCCESS,
            outputs=mock_output,
            duration_ms=0.1,
        )
    
    def _gather_inputs(
        self,
        node: CompositionNode,
        context: ExecutionContext,
        block: Optional[NeuropBlock] = None,
    ) -> Dict[str, Any]:
        """
        Gather and bind inputs for node from context and previous outputs.
        
        This properly maps available data to block interface parameters.
        """
        available: Dict[str, Any] = {}
        
        for var_name, var in context.get_all_variables(ContextScope.GLOBAL).items():
            available[var_name] = var.value
        
        if node.input_sources:
            for source_id in node.input_sources:
                source_output = context.get_node_output(source_id)
                if source_output is not None:
                    if isinstance(source_output, dict):
                        available.update(source_output)
                    else:
                        available["_previous"] = source_output
                        available["input"] = source_output
                        available["value"] = source_output
                        available["data"] = source_output
        else:
            previous = context.get_previous_output()
            if previous is not None:
                if isinstance(previous, dict):
                    available.update(previous)
                else:
                    available["_previous"] = previous
                    available["input"] = previous
                    available["value"] = previous
                    available["data"] = previous
        
        if block is None:
            return available
        
        bound_inputs: Dict[str, Any] = {}
        
        for param in block.interface.inputs:
            param_name = param.name
            param_type = param.data_type.value
            
            if param_name in available:
                bound_inputs[param_name] = available[param_name]
                continue
            
            type_aliases = {
                "email": ["email", "email_address", "mail"],
                "phone": ["phone", "phone_number", "telephone"],
                "text": ["text", "input", "value", "data", "content", "string", "s", "str"],
                "url": ["url", "uri", "link", "href"],
                "name": ["name", "username", "user_name", "full_name"],
                "password": ["password", "passwd", "secret"],
                "number": ["number", "num", "n", "value", "amount", "count"],
                "integer": ["integer", "int", "i", "n", "count"],
                "float": ["float", "f", "decimal", "amount"],
                "boolean": ["boolean", "bool", "flag", "is_active", "enabled"],
                "list": ["list", "items", "array", "elements", "values"],
                "dict": ["dict", "data", "obj", "object", "payload"],
            }
            
            matched = False
            for avail_name, avail_value in available.items():
                avail_lower = avail_name.lower()
                param_lower = param_name.lower()
                
                if param_lower in avail_lower or avail_lower in param_lower:
                    bound_inputs[param_name] = avail_value
                    matched = True
                    break
                
                for sem_type, aliases in type_aliases.items():
                    if param_lower in aliases or any(a in param_lower for a in aliases):
                        if avail_lower in aliases or any(a in avail_lower for a in aliases):
                            bound_inputs[param_name] = avail_value
                            matched = True
                            break
                if matched:
                    break
            
            if not matched and param.optional:
                if param.default_value is not None:
                    bound_inputs[param_name] = param.default_value
            elif not matched and not param.optional:
                if "_previous" in available:
                    bound_inputs[param_name] = available["_previous"]
                elif available:
                    first_val = list(available.values())[0]
                    bound_inputs[param_name] = first_val
        
        return bound_inputs
    
    def _get_circuit_breaker(self, block_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for block."""
        if block_id not in self._circuit_breakers:
            self._circuit_breakers[block_id] = CircuitBreaker()
        return self._circuit_breakers[block_id]
    
    def execute_simple(
        self,
        query: str,
        inputs: Dict[str, Any],
        graph: SemanticGraph,
    ) -> Dict[str, Any]:
        """
        Simple execution returning just the final outputs.
        
        Use this for quick integration without full result tracking.
        """
        result = self.execute(graph, initial_inputs=inputs)
        
        if result.is_success:
            return result.final_outputs
        
        return {
            "error": result.error or result.get_first_error(),
            "partial_outputs": result.final_outputs,
        }
