"""
Golden Validation Suite - Known-Working Blocks

This module provides a curated validation suite using only blocks that are:
1. Single-function (no external dependencies)
2. 100% success rate in testing
3. Deterministic output for given inputs

The golden validation suite proves the full loop:
Intent -> Compose -> Execute -> Result -> Trust Update
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from neurop_forge.core.block_schema import NeuropBlock, DataType
from neurop_forge.runtime.executor import BlockExecutor
from neurop_forge.runtime.trust_tracker import get_trust_tracker


@dataclass
class GoldenBlock:
    """A pre-validated block for the golden validation suite."""
    name: str
    intent: str
    test_input: Dict[str, Any]
    expected_output: Any
    expected_output_type: str


GOLDEN_BLOCKS = [
    GoldenBlock("reverse_string", "reverse a string", {"text": "hello world"}, "dlrow olleh", "string"),
    GoldenBlock("is_empty", "check if empty", {"value": "test"}, False, "boolean"),
    GoldenBlock("to_uppercase", "convert to uppercase", {"text": "hello"}, "HELLO", "string"),
    GoldenBlock("to_lowercase", "convert to lowercase", {"text": "HELLO"}, "hello", "string"),
    GoldenBlock("word_count", "count words", {"text": "hello world test"}, 3, "integer"),
    GoldenBlock("is_not_none", "check if not none", {"value": "test"}, True, "boolean"),
    GoldenBlock("to_integer", "convert to integer", {"value": "42"}, 42, "integer"),
    GoldenBlock("is_positive", "check if positive", {"n": 42}, True, "boolean"),
    GoldenBlock("is_even", "check if even", {"n": 42}, True, "boolean"),
    GoldenBlock("capitalize_first", "capitalize first letter", {"text": "hello"}, "Hello", "string"),
]


class GoldenValidationRunner:
    """Runs the golden validation suite with pre-validated blocks."""

    def __init__(self, block_store):
        self._block_store = block_store
        self._executor = BlockExecutor()
        self._tracker = get_trust_tracker()
        self._validated_blocks: Dict[str, NeuropBlock] = {}

    def discover_golden_blocks(self) -> Dict[str, NeuropBlock]:
        """Discover golden blocks from the library."""
        golden_names = {gb.name for gb in GOLDEN_BLOCKS}
        
        for block in self._block_store.get_all():
            if hasattr(block.metadata, 'name'):
                name = block.metadata.name
                if name in golden_names and name not in self._validated_blocks:
                    if self._is_golden_candidate(block):
                        self._validated_blocks[name] = block

        return self._validated_blocks

    def _is_golden_candidate(self, block: NeuropBlock) -> bool:
        """Check if a block is a candidate for golden validation."""
        if len(block.interface.inputs) == 0:
            return False
        if len(block.interface.inputs) > 2:
            return False
        if not block.logic or not block.logic.strip():
            return False
        if 'import' in block.logic and 'from' in block.logic:
            return False
        return True

    def run_golden_validation(self) -> Dict[str, Any]:
        """Run the complete golden validation suite."""
        results = {
            "blocks_tested": 0,
            "blocks_succeeded": 0,
            "blocks_failed": 0,
            "execution_traces": [],
            "trust_stats": [],
        }

        self.discover_golden_blocks()

        for golden in GOLDEN_BLOCKS:
            if golden.name not in self._validated_blocks:
                continue

            block = self._validated_blocks[golden.name]
            
            param_names = [p.name for p in block.interface.inputs]
            inputs = {}
            for pname in param_names:
                for key, val in golden.test_input.items():
                    if key == pname or key.lower() == pname.lower():
                        inputs[pname] = val
                        break
                else:
                    first_val = list(golden.test_input.values())[0]
                    inputs[pname] = first_val

            outputs, error = self._executor.execute(block, inputs)
            
            results["blocks_tested"] += 1
            
            actual_result = None
            output_correct = False
            if error is None and outputs:
                actual_result = outputs.get("result", list(outputs.values())[0] if outputs else None)
                output_correct = actual_result == golden.expected_output
            
            success = error is None and output_correct
            
            if success:
                results["blocks_succeeded"] += 1
            else:
                results["blocks_failed"] += 1
                if error is None and not output_correct:
                    error = f"Output mismatch: expected {golden.expected_output!r}, got {actual_result!r}"

            trace = {
                "block_name": golden.name,
                "intent": golden.intent,
                "inputs": inputs,
                "outputs": outputs if error is None else None,
                "expected": golden.expected_output,
                "actual": actual_result,
                "output_correct": output_correct,
                "error": error,
                "success": success,
            }
            results["execution_traces"].append(trace)

            block_hash = block.identity.get('content_hash', golden.name) if isinstance(block.identity, dict) else golden.name
            stats = self._tracker.get_execution_stats(str(block_hash))
            if stats:
                results["trust_stats"].append({
                    "block_name": golden.name,
                    "execution_count": stats.execution_count,
                    "success_rate": stats.success_rate,
                    "avg_duration_ms": stats.avg_duration_ms,
                })

        return results

    def run_string_pipeline(self) -> Dict[str, Any]:
        """String normalization pipeline (trim -> lowercase -> word_count)."""
        result = {
            "pipeline": "string_normalization",
            "stages": [],
            "final_output": None,
        }

        input_text = "  Hello World Test  "
        current_value = input_text

        stages = [
            ("to_lowercase", {"text": current_value}),
        ]

        if "to_lowercase" in self._validated_blocks:
            block = self._validated_blocks["to_lowercase"]
            outputs, error = self._executor.execute(block, {"text": current_value})
            if not error:
                current_value = outputs.get("result", outputs.get("text", current_value))
                result["stages"].append({
                    "stage": "to_lowercase",
                    "input": input_text,
                    "output": current_value,
                    "success": True,
                })

        if "word_count" in self._validated_blocks:
            block = self._validated_blocks["word_count"]
            param_name = block.interface.inputs[0].name if block.interface.inputs else "text"
            outputs, error = self._executor.execute(block, {param_name: current_value})
            if not error:
                word_ct = outputs.get("result", outputs.get("count", 0))
                result["stages"].append({
                    "stage": "word_count",
                    "input": current_value,
                    "output": word_ct,
                    "success": True,
                })
                result["final_output"] = word_ct

        return result


def run_golden_validation(block_store) -> Dict[str, Any]:
    """Convenience function to run the golden validation suite."""
    runner = GoldenValidationRunner(block_store)
    results = runner.run_golden_validation()
    pipeline_result = runner.run_string_pipeline()
    
    return {
        "golden_blocks": results,
        "pipeline_result": pipeline_result,
    }


def print_golden_validation_results(results: Dict[str, Any]) -> None:
    """Print golden validation results in a formatted way."""
    print()
    print("=" * 60)
    print("GOLDEN VALIDATION SUITE - Known-Working Blocks")
    print("=" * 60)
    print()

    golden = results.get("golden_blocks", {})
    print(f"Blocks Tested: {golden.get('blocks_tested', 0)}")
    print(f"Blocks Succeeded: {golden.get('blocks_succeeded', 0)}")
    print(f"Blocks Failed: {golden.get('blocks_failed', 0)}")
    print()

    print("Execution Traces:")
    print("-" * 40)
    for trace in golden.get("execution_traces", []):
        status = "SUCCESS" if trace["success"] else "FAILED"
        print(f"  {trace['block_name']}: {status}")
        if trace["success"]:
            print(f"    Expected: {trace.get('expected')!r} -> Got: {trace.get('actual')!r}")
        else:
            err_msg = trace["error"][:60] if trace.get("error") else "Unknown"
            print(f"    Error: {err_msg}")
    print()

    if golden.get("trust_stats"):
        print("Trust Tracking Stats:")
        print("-" * 40)
        print(f"  {'Block Name':<20} {'Execs':>6} {'Success%':>8} {'Avg ms':>8}")
        print(f"  {'-'*20} {'-'*6} {'-'*8} {'-'*8}")
        for stat in golden["trust_stats"]:
            print(f"  {stat['block_name']:<20} {stat['execution_count']:>6} {stat['success_rate']*100:>7.1f}% {stat['avg_duration_ms']:>8.2f}")
    print()

    pipeline = results.get("pipeline_result", {})
    if pipeline.get("stages"):
        print("Pipeline Execution: String Normalization")
        print("-" * 40)
        for stage in pipeline["stages"]:
            print(f"  {stage['stage']}: {stage['input']} -> {stage['output']}")
        print(f"  Final Result: {pipeline.get('final_output')}")
    print()
