"""
Neurop Block Forge v1.0.0 - Public API

Clean interface for block execution, workflow composition, and block discovery.
Production-grade with 2,060+ Tier-A deterministic blocks.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json

from neurop_forge.core.block_schema import NeuropBlock
from neurop_forge.library.block_store import BlockStore
from neurop_forge.runtime.executor import BlockExecutor
from neurop_forge.runtime.reference_workflows import (
    ReferenceWorkflowRunner,
    REFERENCE_WORKFLOWS,
)


class NeuropForge:
    """
    Main API for Neurop Block Forge.
    
    Provides clean interface for:
    - Executing verified blocks
    - Running reference workflows
    - Discovering available blocks
    
    Example:
        forge = NeuropForge()
        
        result = forge.execute_block("reverse_string", {"s": "hello"})
        print(result)  # {'result': 'olleh', 'success': True}
        
        blocks = forge.list_verified_blocks(category="string")
        print(f"Found {len(blocks)} string blocks")
        
        workflow = forge.run_workflow("text_normalization", {"text": "Hello World"})
        print(workflow)
    """
    
    def __init__(self, auto_load: bool = True):
        """
        Initialize Neurop Forge.
        
        Args:
            auto_load: If True, automatically load the block library.
        """
        self._block_store = BlockStore(storage_path=".neurop_expanded_library")
        self._executor = BlockExecutor()
        self._verified_ids: set = set()
        self._tier_a_ids: set = set()
        self._name_to_id: Dict[str, str] = {}
        self._initialized = False
        
        if auto_load:
            self._load_registries()
    
    def _load_registries(self) -> None:
        """Load verified and tier registries from disk."""
        registry_path = Path(".neurop_verified/registry.json")
        tier_registry_path = Path(".neurop_verified/tier_registry.json")
        
        if registry_path.exists():
            with open(registry_path) as f:
                registry_data = json.load(f)
            for block_id, block_data in registry_data.get("verified_blocks", {}).items():
                self._verified_ids.add(block_id)
                if "block_name" in block_data:
                    self._name_to_id[block_data["block_name"]] = block_id
        
        if tier_registry_path.exists():
            with open(tier_registry_path) as f:
                tier_data = json.load(f)
                self._tier_a_ids = set(tier_data.get("tier_a", []))
        
        for block_id, block in self._block_store._blocks.items():
            name = block.metadata.name
            if name and block_id not in self._name_to_id.values():
                self._name_to_id[name] = block_id
        
        self._initialized = True
    
    def _resolve_block_id(self, block_id_or_name: str) -> str:
        """Resolve a block name or ID to its ID."""
        if block_id_or_name in self._block_store._blocks:
            return block_id_or_name
        if block_id_or_name in self._name_to_id:
            return self._name_to_id[block_id_or_name]
        raise ValueError(f"Block '{block_id_or_name}' not found.")
    
    def execute_block(
        self,
        block_id_or_name: str,
        inputs: Dict[str, Any],
        tier_a_only: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a verified block with the given inputs.
        
        Args:
            block_id_or_name: Block ID or name (e.g., "reverse_string").
            inputs: Dictionary of input values.
            tier_a_only: If True (default), only execute Tier-A deterministic blocks.
        
        Returns:
            Dictionary with execution result:
            - 'result': The block's output value
            - 'success': Boolean indicating execution success
            - 'error': Error message if execution failed (optional)
        
        Example:
            result = forge.execute_block("reverse_string", {"s": "hello"})
            # Returns: {'result': 'olleh', 'success': True}
        """
        if not self._initialized:
            raise RuntimeError("Forge not initialized.")
        
        block_id = self._resolve_block_id(block_id_or_name)
        
        if block_id not in self._verified_ids:
            raise ValueError(f"Block '{block_id_or_name}' is not verified.")
        
        if tier_a_only and block_id not in self._tier_a_ids:
            raise ValueError(
                f"Block '{block_id_or_name}' is Tier-B (context-dependent). "
                "Set tier_a_only=False to execute."
            )
        
        block = self._block_store._blocks.get(block_id)
        if not block:
            raise ValueError(f"Block '{block_id_or_name}' not found in store.")
        
        try:
            outputs, error = self._executor.execute(block, inputs)
            if error:
                return {"result": None, "success": False, "error": error}
            result = outputs.get("result", outputs.get("output", outputs))
            return {"result": result, "success": True}
        except Exception as e:
            return {"result": None, "success": False, "error": str(e)}
    
    def run_workflow(
        self,
        workflow_id: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a reference workflow.
        
        Args:
            workflow_id: ID of the workflow to run. Available workflows:
                        - text_normalization
                        - string_analysis
                        - data_extraction
                        - input_validation
                        - text_transform_chain
            inputs: Optional input dictionary.
        
        Returns:
            Dictionary with workflow execution result.
        
        Example:
            result = forge.run_workflow("text_normalization", {"text": "Hello World"})
        """
        if not self._initialized:
            raise RuntimeError("Forge not initialized.")
        
        runner = ReferenceWorkflowRunner(self._block_store)
        
        available_ids = [w.id for w in runner.get_available_workflows()]
        if workflow_id not in available_ids:
            raise ValueError(
                f"Workflow '{workflow_id}' not available. "
                f"Available: {available_ids}"
            )
        
        result = runner.execute_workflow(workflow_id, inputs)
        
        return {
            "success": result.success,
            "steps_executed": result.steps_executed,
            "steps_succeeded": result.steps_succeeded,
            "duration_ms": result.duration_ms,
            "outputs": result.outputs
        }
    
    def list_verified_blocks(
        self,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List verified blocks with optional filtering.
        
        Args:
            category: Filter by category (string, validation, collection, etc.)
            tier: Filter by tier ('A' for deterministic, 'B' for context-dependent)
            limit: Maximum number of blocks to return (default 100)
        
        Returns:
            List of block metadata dictionaries.
        
        Example:
            string_blocks = forge.list_verified_blocks(category="string", tier="A")
        """
        if not self._initialized:
            raise RuntimeError("Forge not initialized.")
        
        results = []
        for block_id in self._verified_ids:
            block = self._block_store._blocks.get(block_id)
            if not block:
                continue
            
            block_tier = "A" if block_id in self._tier_a_ids else "B"
            
            if tier and tier.upper() != block_tier:
                continue
            
            block_category = block.metadata.category if block.metadata else "utility"
            if category and block_category != category:
                continue
            
            results.append({
                "id": block_id,
                "name": block.metadata.name if block.metadata else block_id[:8],
                "description": block.metadata.description if block.metadata else "",
                "category": block_category,
                "tier": block_tier
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List available reference workflows.
        
        Returns:
            List of workflow metadata dictionaries.
        """
        runner = ReferenceWorkflowRunner(self._block_store)
        available = runner.get_available_workflows()
        
        return [
            {
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "steps": len(wf.steps)
            }
            for wf in available
        ]
    
    def get_block_info(self, block_id_or_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific block.
        
        Args:
            block_id_or_name: Block ID or name.
        
        Returns:
            Dictionary with block details.
        """
        block_id = self._resolve_block_id(block_id_or_name)
        block = self._block_store._blocks.get(block_id)
        
        if not block:
            raise ValueError(f"Block '{block_id_or_name}' not found.")
        
        return {
            "id": block_id,
            "name": block.metadata.name if block.metadata else block_id[:8],
            "description": block.metadata.description if block.metadata else "",
            "category": block.metadata.category if block.metadata else "utility",
            "tier": "A" if block_id in self._tier_a_ids else "B",
            "verified": block_id in self._verified_ids,
            "interface": {
                "inputs": [p.to_dict() for p in block.interface.inputs] if block.interface else [],
                "outputs": [p.to_dict() for p in block.interface.outputs] if block.interface else []
            }
        }
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get library statistics."""
        verified_tier_a = len(self._verified_ids & self._tier_a_ids)
        verified_tier_b = len(self._verified_ids) - verified_tier_a
        return {
            "total_blocks": len(self._block_store._blocks),
            "total_verified": len(self._verified_ids),
            "tier_a": verified_tier_a,
            "tier_b": verified_tier_b
        }


def execute_block(block_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to execute a block.
    
    Example:
        from neurop_forge import execute_block
        result = execute_block("reverse_string", {"s": "hello"})
    """
    forge = NeuropForge()
    return forge.execute_block(block_id, inputs)


def run_workflow(workflow_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to run a workflow.
    
    Example:
        from neurop_forge import run_workflow
        result = run_workflow("text_normalization", {"text": "Hello World"})
    """
    forge = NeuropForge()
    return forge.run_workflow(workflow_id, inputs)


def list_blocks(category: Optional[str] = None, tier: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to list blocks.
    
    Example:
        from neurop_forge import list_blocks
        blocks = list_blocks(category="string", tier="A")
    """
    forge = NeuropForge()
    return forge.list_verified_blocks(category=category, tier=tier)
