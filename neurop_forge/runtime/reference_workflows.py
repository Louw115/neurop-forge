"""
Copyright 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Production Reference Workflows - Proven Semantic Graphs

This module provides 5 production-ready workflow templates that:
1. Use ONLY verified blocks (from the verified registry)
2. Demonstrate real-world use cases
3. Serve as proof points for the system
4. Act as templates for custom workflow creation

Each workflow is a semantic graph that can be executed end-to-end.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from neurop_forge.core.block_schema import NeuropBlock, DataType
from neurop_forge.runtime.executor import BlockExecutor, GraphExecutor
from neurop_forge.runtime.block_verifier import BlockVerifier, get_verification_registry
from neurop_forge.runtime.trust_tracker import get_trust_tracker


class WorkflowCategory(Enum):
    TEXT_PROCESSING = "text_processing"
    DATA_VALIDATION = "data_validation"
    NUMERIC_COMPUTATION = "numeric_computation"
    DATA_TRANSFORMATION = "data_transformation"
    USER_INPUT = "user_input"


@dataclass
class WorkflowStep:
    """A single step in a reference workflow."""
    name: str
    block_name: str
    input_mapping: Dict[str, str]
    description: str


@dataclass
class ReferenceWorkflow:
    """A production reference workflow definition."""
    id: str
    name: str
    description: str
    category: WorkflowCategory
    steps: List[WorkflowStep]
    test_inputs: Dict[str, Any]
    expected_behavior: str


@dataclass
class WorkflowExecutionResult:
    """Result of executing a reference workflow."""
    workflow_id: str
    success: bool
    steps_executed: int
    steps_succeeded: int
    duration_ms: float
    outputs: Dict[str, Any]
    step_traces: List[Dict[str, Any]]
    error: Optional[str] = None


REFERENCE_WORKFLOWS = [
    ReferenceWorkflow(
        id="text_normalization",
        name="Text Normalization Pipeline",
        description="Normalize user text input: lowercase, trim, validate non-empty",
        category=WorkflowCategory.TEXT_PROCESSING,
        steps=[
            WorkflowStep("lowercase", "to_lowercase", {"text": "input"}, "Convert to lowercase"),
            WorkflowStep("check_empty", "is_empty", {"value": "lowercase.result"}, "Check if empty"),
            WorkflowStep("word_count", "word_count", {"text": "lowercase.result"}, "Count words"),
        ],
        test_inputs={"input": "  Hello World TEST  "},
        expected_behavior="Returns lowercase text with word count, validates non-empty"
    ),
    ReferenceWorkflow(
        id="string_analysis",
        name="String Analysis Pipeline",
        description="Analyze string properties: reverse, check palindrome, get length",
        category=WorkflowCategory.TEXT_PROCESSING,
        steps=[
            WorkflowStep("reverse", "reverse_string", {"text": "input"}, "Reverse the string"),
            WorkflowStep("uppercase", "to_uppercase", {"text": "input"}, "Convert to uppercase"),
            WorkflowStep("capitalize", "capitalize_first", {"text": "input"}, "Capitalize first letter"),
        ],
        test_inputs={"input": "hello world"},
        expected_behavior="Returns reversed string, uppercase version, and capitalized version"
    ),
    ReferenceWorkflow(
        id="data_extraction",
        name="Data Extraction Pipeline",
        description="Extract and validate data: check not none, get type, validate",
        category=WorkflowCategory.DATA_VALIDATION,
        steps=[
            WorkflowStep("check_exists", "is_not_none", {"value": "input"}, "Check value exists"),
            WorkflowStep("normalize", "to_lowercase", {"text": "input"}, "Normalize text"),
            WorkflowStep("reverse_check", "reverse_string", {"text": "normalize.result"}, "Reverse for verification"),
        ],
        test_inputs={"input": "TestData"},
        expected_behavior="Validates data exists, normalizes, and reverses for verification"
    ),
    ReferenceWorkflow(
        id="input_validation",
        name="User Input Validation Pipeline",
        description="Validate user input: non-null, non-empty, type check",
        category=WorkflowCategory.USER_INPUT,
        steps=[
            WorkflowStep("not_none", "is_not_none", {"value": "input"}, "Check not null"),
            WorkflowStep("not_empty", "is_empty", {"value": "input"}, "Check not empty"),
            WorkflowStep("lowercase", "to_lowercase", {"text": "input"}, "Normalize to lowercase"),
        ],
        test_inputs={"input": "User@Example.COM"},
        expected_behavior="Validates input exists, not empty, returns normalized lowercase"
    ),
    ReferenceWorkflow(
        id="text_transform_chain",
        name="Text Transform Chain",
        description="Chain multiple text transformations: capitalize, reverse, check",
        category=WorkflowCategory.DATA_TRANSFORMATION,
        steps=[
            WorkflowStep("capitalize", "capitalize_first", {"text": "input"}, "Capitalize first"),
            WorkflowStep("reverse", "reverse_string", {"text": "capitalize.result"}, "Reverse capitalized"),
            WorkflowStep("check", "is_empty", {"value": "reverse.result"}, "Verify non-empty"),
        ],
        test_inputs={"input": "hello"},
        expected_behavior="Capitalizes, reverses, validates result exists"
    ),
]


class ReferenceWorkflowRunner:
    """Executes production reference workflows using verified blocks."""

    def __init__(self, block_store):
        self._block_store = block_store
        self._executor = BlockExecutor()
        self._registry = get_verification_registry()
        self._tracker = get_trust_tracker()
        self._verified_blocks: Dict[str, NeuropBlock] = {}
        self._discover_verified_blocks()

    def _discover_verified_blocks(self) -> None:
        """Discover all verified blocks from the store."""
        verified_ids = set(self._registry.get_verified_ids())
        
        for block in self._block_store.get_all():
            block_id = block.get_identity_hash()
            if block_id in verified_ids:
                if hasattr(block.metadata, 'name'):
                    self._verified_blocks[block.metadata.name] = block

    def get_verified_block_count(self) -> int:
        """Get count of discovered verified blocks."""
        return len(self._verified_blocks)

    def get_available_workflows(self) -> List[ReferenceWorkflow]:
        """Get list of workflows that can be executed with available blocks."""
        available = []
        for workflow in REFERENCE_WORKFLOWS:
            can_execute = True
            for step in workflow.steps:
                if step.block_name not in self._verified_blocks:
                    can_execute = False
                    break
            if can_execute:
                available.append(workflow)
        return available

    def execute_workflow(self, workflow_id: str, custom_inputs: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResult:
        """Execute a reference workflow by ID."""
        workflow = None
        for w in REFERENCE_WORKFLOWS:
            if w.id == workflow_id:
                workflow = w
                break
        
        if not workflow:
            return WorkflowExecutionResult(
                workflow_id=workflow_id,
                success=False,
                steps_executed=0,
                steps_succeeded=0,
                duration_ms=0,
                outputs={},
                step_traces=[],
                error=f"Workflow '{workflow_id}' not found"
            )
        
        return self._execute(workflow, custom_inputs)

    def _execute(self, workflow: ReferenceWorkflow, custom_inputs: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResult:
        """Execute a workflow with step-by-step tracing."""
        import time
        start_time = time.perf_counter()
        
        inputs = custom_inputs if custom_inputs else workflow.test_inputs
        context = dict(inputs)
        if "input" in inputs:
            context["input"] = inputs["input"]
        else:
            context["input"] = inputs
        step_traces = []
        steps_succeeded = 0
        
        for step in workflow.steps:
            if step.block_name not in self._verified_blocks:
                step_traces.append({
                    "step": step.name,
                    "block": step.block_name,
                    "status": "skipped",
                    "error": f"Block '{step.block_name}' not verified"
                })
                continue
            
            block = self._verified_blocks[step.block_name]
            
            step_inputs = {}
            for param_name, source in step.input_mapping.items():
                if "." in source:
                    source_step, source_key = source.split(".", 1)
                    if source_step in context and isinstance(context[source_step], dict):
                        step_inputs[param_name] = context[source_step].get(source_key, context[source_step])
                    else:
                        step_inputs[param_name] = context.get(source_step, "")
                else:
                    step_inputs[param_name] = context.get(source, inputs.get(source, ""))
            
            actual_inputs = {}
            for param in block.interface.inputs:
                for k, v in step_inputs.items():
                    if k == param.name or k.lower() == param.name.lower():
                        actual_inputs[param.name] = v
                        break
                else:
                    if step_inputs:
                        actual_inputs[param.name] = list(step_inputs.values())[0]
            
            step_start = time.perf_counter()
            outputs, error = self._executor.execute(block, actual_inputs)
            step_duration = (time.perf_counter() - step_start) * 1000
            
            if error:
                step_traces.append({
                    "step": step.name,
                    "block": step.block_name,
                    "status": "failed",
                    "inputs": actual_inputs,
                    "error": error,
                    "duration_ms": step_duration
                })
            else:
                steps_succeeded += 1
                context[step.name] = outputs
                step_traces.append({
                    "step": step.name,
                    "block": step.block_name,
                    "status": "success",
                    "inputs": actual_inputs,
                    "outputs": outputs,
                    "duration_ms": step_duration
                })
        
        total_duration = (time.perf_counter() - start_time) * 1000
        
        final_outputs = {}
        for step_name, step_output in context.items():
            if step_name != "input" and isinstance(step_output, dict):
                final_outputs[step_name] = step_output
        
        return WorkflowExecutionResult(
            workflow_id=workflow.id,
            success=steps_succeeded == len(workflow.steps),
            steps_executed=len(workflow.steps),
            steps_succeeded=steps_succeeded,
            duration_ms=total_duration,
            outputs=final_outputs,
            step_traces=step_traces
        )

    def run_all_workflows(self) -> Dict[str, WorkflowExecutionResult]:
        """Execute all available reference workflows."""
        results = {}
        for workflow in self.get_available_workflows():
            results[workflow.id] = self.execute_workflow(workflow.id)
        return results


def run_reference_workflows(block_store) -> Dict[str, Any]:
    """Convenience function to run all reference workflows."""
    runner = ReferenceWorkflowRunner(block_store)
    
    available = runner.get_available_workflows()
    results = runner.run_all_workflows()
    
    summary = {
        "verified_blocks_discovered": runner.get_verified_block_count(),
        "workflows_available": len(available),
        "workflows_total": len(REFERENCE_WORKFLOWS),
        "results": {},
        "overall_success": True,
    }
    
    for wf_id, result in results.items():
        summary["results"][wf_id] = {
            "success": result.success,
            "steps": f"{result.steps_succeeded}/{result.steps_executed}",
            "duration_ms": result.duration_ms,
        }
        if not result.success:
            summary["overall_success"] = False
    
    return summary


def print_reference_workflow_results(summary: Dict[str, Any]) -> None:
    """Print reference workflow results in formatted output."""
    print()
    print("=" * 60)
    print("PRODUCTION REFERENCE WORKFLOWS")
    print("=" * 60)
    print()
    print(f"Verified Blocks Available: {summary['verified_blocks_discovered']}")
    print(f"Workflows Executable: {summary['workflows_available']}/{summary['workflows_total']}")
    print()
    print("Workflow Execution Results:")
    print("-" * 40)
    
    for wf_id, result in summary.get("results", {}).items():
        status = "PASS" if result["success"] else "FAIL"
        print(f"  [{status}] {wf_id}: {result['steps']} steps ({result['duration_ms']:.2f}ms)")
    
    print()
    overall = "ALL PASSED" if summary["overall_success"] else "SOME FAILED"
    print(f"Overall: {overall}")
    print()
