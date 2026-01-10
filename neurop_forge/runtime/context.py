"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

ExecutionContext - Manages runtime state, variables, and data flow.

The ExecutionContext is the memory of graph execution:
- Stores input/output values between blocks
- Manages variable scopes (global, graph, node)
- Tracks execution history for debugging
- Provides type-safe variable access
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import copy
import hashlib
import json


class ContextScope(Enum):
    """Variable scope levels."""
    GLOBAL = "global"
    GRAPH = "graph"
    NODE = "node"
    TEMPORARY = "temporary"


@dataclass
class ExecutionVariable:
    """A typed variable in the execution context."""
    name: str
    value: Any
    data_type: str
    scope: ContextScope
    source_node: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_readonly: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self._serialize_value(self.value),
            "data_type": self.data_type,
            "scope": self.scope.value,
            "source_node": self.source_node,
            "created_at": self.created_at,
            "is_readonly": self.is_readonly,
        }
    
    def _serialize_value(self, val: Any) -> Any:
        """Serialize value for storage."""
        if isinstance(val, (str, int, float, bool, type(None))):
            return val
        if isinstance(val, (list, tuple)):
            return [self._serialize_value(v) for v in val]
        if isinstance(val, dict):
            return {k: self._serialize_value(v) for k, v in val.items()}
        return str(val)


@dataclass
class ContextCheckpoint:
    """A snapshot of context state for rollback."""
    checkpoint_id: str
    timestamp: str
    variables: Dict[str, ExecutionVariable]
    node_position: int
    reason: str


class ExecutionContext:
    """
    Runtime execution context for graph execution.
    
    Features:
    - Scoped variable management (global, graph, node)
    - Type tracking for all values
    - Checkpointing for rollback
    - Data flow tracking between nodes
    - Immutable input handling
    """
    
    def __init__(
        self,
        initial_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self._variables: Dict[str, ExecutionVariable] = {}
        self._checkpoints: List[ContextCheckpoint] = []
        self._history: List[Dict[str, Any]] = []
        self._config = config or {}
        self._execution_id = self._generate_execution_id()
        self._current_node: Optional[str] = None
        self._node_outputs: Dict[str, Dict[str, Any]] = {}
        
        if initial_inputs:
            for name, value in initial_inputs.items():
                self.set(
                    name=name,
                    value=value,
                    scope=ContextScope.GLOBAL,
                    is_readonly=True,
                )
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID."""
        data = f"{datetime.now().isoformat()}-{id(self)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    @property
    def execution_id(self) -> str:
        return self._execution_id
    
    def set(
        self,
        name: str,
        value: Any,
        scope: ContextScope = ContextScope.GRAPH,
        data_type: Optional[str] = None,
        source_node: Optional[str] = None,
        is_readonly: bool = False,
    ) -> None:
        """Set a variable in the context."""
        if name in self._variables and self._variables[name].is_readonly:
            raise ValueError(f"Cannot modify readonly variable: {name}")
        
        inferred_type = data_type or self._infer_type(value)
        
        var = ExecutionVariable(
            name=name,
            value=value,
            data_type=inferred_type,
            scope=scope,
            source_node=source_node or self._current_node,
            is_readonly=is_readonly,
        )
        
        self._variables[name] = var
        
        self._history.append({
            "action": "set",
            "name": name,
            "scope": scope.value,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get a variable value from the context."""
        var = self._variables.get(name)
        if var is None:
            return default
        return var.value
    
    def get_typed(self, name: str) -> Optional[ExecutionVariable]:
        """Get the full typed variable."""
        return self._variables.get(name)
    
    def has(self, name: str) -> bool:
        """Check if variable exists."""
        return name in self._variables
    
    def delete(self, name: str) -> bool:
        """Delete a variable if not readonly."""
        var = self._variables.get(name)
        if var is None:
            return False
        if var.is_readonly:
            raise ValueError(f"Cannot delete readonly variable: {name}")
        
        del self._variables[name]
        self._history.append({
            "action": "delete",
            "name": name,
            "timestamp": datetime.now().isoformat(),
        })
        return True
    
    def set_node_output(
        self,
        node_id: str,
        outputs: Dict[str, Any],
    ) -> None:
        """Store outputs from a node execution."""
        self._node_outputs[node_id] = outputs
        
        for name, value in outputs.items():
            output_name = f"{node_id}.{name}"
            self.set(
                name=output_name,
                value=value,
                scope=ContextScope.GRAPH,
                source_node=node_id,
            )
    
    def get_node_output(
        self,
        node_id: str,
        output_name: Optional[str] = None,
    ) -> Any:
        """Get output from a specific node."""
        node_outputs = self._node_outputs.get(node_id, {})
        
        if output_name:
            return node_outputs.get(output_name)
        
        if len(node_outputs) == 1:
            return list(node_outputs.values())[0]
        
        return node_outputs
    
    def get_previous_output(self) -> Any:
        """Get the most recent node output (for chaining)."""
        if not self._node_outputs:
            return None
        
        last_node = list(self._node_outputs.keys())[-1]
        return self.get_node_output(last_node)
    
    def enter_node(self, node_id: str) -> None:
        """Enter a node scope."""
        self._current_node = node_id
    
    def exit_node(self) -> None:
        """Exit node scope and clean temporary variables."""
        temp_vars = [
            name for name, var in self._variables.items()
            if var.scope == ContextScope.TEMPORARY
        ]
        for name in temp_vars:
            del self._variables[name]
        
        self._current_node = None
    
    def checkpoint(self, reason: str = "manual") -> str:
        """Create a checkpoint for potential rollback."""
        checkpoint_id = f"cp_{len(self._checkpoints)}_{datetime.now().strftime('%H%M%S')}"
        
        cp = ContextCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            variables=copy.deepcopy(self._variables),
            node_position=len(self._node_outputs),
            reason=reason,
        )
        
        self._checkpoints.append(cp)
        return checkpoint_id
    
    def rollback(self, checkpoint_id: str) -> bool:
        """Rollback to a specific checkpoint."""
        for cp in reversed(self._checkpoints):
            if cp.checkpoint_id == checkpoint_id:
                self._variables = copy.deepcopy(cp.variables)
                
                nodes_to_remove = list(self._node_outputs.keys())[cp.node_position:]
                for node_id in nodes_to_remove:
                    del self._node_outputs[node_id]
                
                self._history.append({
                    "action": "rollback",
                    "checkpoint_id": checkpoint_id,
                    "timestamp": datetime.now().isoformat(),
                })
                return True
        
        return False
    
    def get_all_variables(
        self,
        scope: Optional[ContextScope] = None
    ) -> Dict[str, ExecutionVariable]:
        """Get all variables, optionally filtered by scope."""
        if scope is None:
            return dict(self._variables)
        
        return {
            name: var for name, var in self._variables.items()
            if var.scope == scope
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution context summary."""
        return {
            "execution_id": self._execution_id,
            "variable_count": len(self._variables),
            "node_count": len(self._node_outputs),
            "checkpoint_count": len(self._checkpoints),
            "variables": {
                name: var.to_dict() for name, var in self._variables.items()
            },
            "node_outputs": list(self._node_outputs.keys()),
        }
    
    def _infer_type(self, value: Any) -> str:
        """Infer data type from value."""
        if value is None:
            return "none"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "dict"
        if isinstance(value, bytes):
            return "bytes"
        return "any"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "execution_id": self._execution_id,
            "variables": {n: v.to_dict() for n, v in self._variables.items()},
            "node_outputs": self._node_outputs,
            "checkpoints": [
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "timestamp": cp.timestamp,
                    "reason": cp.reason,
                }
                for cp in self._checkpoints
            ],
            "history": self._history[-100:],
        }
