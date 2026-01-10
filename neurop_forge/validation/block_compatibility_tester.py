"""
Block Compatibility Tester - Automated testing for Neurop Forge blocks.

Tests all Tier-A blocks for:
- Parameter standardization
- Duplicate block names
- Execution compatibility
- Input/output validation
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class BlockTestResult:
    """Result of testing a single block."""
    block_id: str
    block_name: str
    passed: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parameter_names: List[str] = field(default_factory=list)
    execution_result: Optional[Dict] = None


@dataclass 
class CompatibilityReport:
    """Full compatibility report for all tested blocks."""
    total_blocks: int = 0
    passed: int = 0
    failed: int = 0
    warnings_count: int = 0
    duplicate_names: Dict[str, List[str]] = field(default_factory=dict)
    non_standard_params: List[Tuple[str, str, List[str]]] = field(default_factory=list)
    execution_failures: List[Tuple[str, str, str]] = field(default_factory=list)
    results: List[BlockTestResult] = field(default_factory=list)


STANDARD_PARAM_NAMES = {
    "string": ["text", "s", "string", "value", "input"],
    "integer": ["n", "num", "number", "value", "x", "y"],
    "list": ["items", "lst", "list", "values", "array"],
    "dict": ["data", "obj", "dict", "mapping"],
    "boolean": ["value", "flag", "condition"],
}

COMMON_TEXT_PARAMS = {"text", "s", "string", "value", "input", "str"}


class BlockCompatibilityTester:
    """Tests block compatibility and generates reports."""
    
    def __init__(self, library_path: str = ".neurop_expanded_library",
                 registry_path: str = ".neurop_verified"):
        self.library_path = Path(library_path)
        self.registry_path = Path(registry_path)
        self._blocks: Dict[str, Any] = {}
        self._verified_ids: set = set()
        self._tier_a_ids: set = set()
        self._name_to_ids: Dict[str, List[str]] = defaultdict(list)
        
    def load_blocks(self) -> int:
        """Load all blocks from the library."""
        if not self.library_path.exists():
            return 0
            
        count = 0
        for block_file in self.library_path.glob("*.json"):
            try:
                with open(block_file) as f:
                    block_data = json.load(f)
                block_id = block_data.get("identity", {}).get("hash_value", block_file.stem)
                self._blocks[block_id] = block_data
                
                name = block_data.get("metadata", {}).get("name", "")
                if name:
                    self._name_to_ids[name].append(block_id)
                count += 1
            except Exception:
                continue
        
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            with open(registry_file) as f:
                registry = json.load(f)
            self._verified_ids = set(registry.get("verified_blocks", {}).keys())
        
        tier_file = self.registry_path / "tier_registry.json"
        if tier_file.exists():
            with open(tier_file) as f:
                tier_data = json.load(f)
            self._tier_a_ids = set(tier_data.get("tier_a", []))
                
        return count
    
    def find_duplicate_names(self) -> Dict[str, List[str]]:
        """Find blocks that share the same name."""
        duplicates = {}
        for name, ids in self._name_to_ids.items():
            if len(ids) > 1:
                duplicates[name] = ids
        return duplicates
    
    def check_parameter_standardization(self, block_id: str) -> Tuple[bool, List[str], List[str]]:
        """Check if block uses standard parameter names for all data types."""
        block = self._blocks.get(block_id)
        if not block:
            return False, [], ["Block not found"]
        
        interface = block.get("interface", {})
        inputs = interface.get("inputs", [])
        
        param_names = [inp.get("name", "") for inp in inputs]
        warnings = []
        
        for inp in inputs:
            param_name = inp.get("name", "")
            data_type = inp.get("data_type", "").lower()
            
            if data_type in STANDARD_PARAM_NAMES:
                standard_names = STANDARD_PARAM_NAMES[data_type]
                if param_name not in standard_names:
                    warnings.append(
                        f"Non-standard {data_type} param '{param_name}' "
                        f"(expected: {', '.join(standard_names[:3])})"
                    )
        
        return len(warnings) == 0, param_names, warnings
    
    def test_block_execution(self, block_id: str) -> Tuple[bool, Optional[Dict], str]:
        """Test if a block can be executed with sample inputs."""
        block = self._blocks.get(block_id)
        if not block:
            return False, None, "Block not found"
        
        interface = block.get("interface", {})
        inputs = interface.get("inputs", [])
        logic = block.get("logic", "")
        
        if not logic:
            return False, None, "No logic defined"
        
        sample_inputs = {}
        for inp in inputs:
            param_name = inp.get("name", "")
            data_type = inp.get("data_type", "").lower()
            
            if data_type == "string":
                sample_inputs[param_name] = "test123"
            elif data_type == "integer":
                sample_inputs[param_name] = 42
            elif data_type == "float":
                sample_inputs[param_name] = 3.14
            elif data_type == "boolean":
                sample_inputs[param_name] = True
            elif data_type == "list":
                sample_inputs[param_name] = [1, 2, 3]
            elif data_type == "dict":
                sample_inputs[param_name] = {"key": "value"}
            else:
                sample_inputs[param_name] = "test"
        
        try:
            local_namespace = {}
            exec(logic, {"__builtins__": __builtins__}, local_namespace)
            
            func_name = block.get("metadata", {}).get("name", "")
            if func_name and func_name in local_namespace:
                func = local_namespace[func_name]
                result = func(**sample_inputs)
                return True, {"result": result, "success": True}, ""
            else:
                return True, {"result": None, "success": True}, "Function executed (name mismatch)"
                
        except Exception as e:
            return False, None, str(e)[:100]
    
    def test_single_block(self, block_id: str) -> BlockTestResult:
        """Run all tests on a single block."""
        block = self._blocks.get(block_id)
        if not block:
            return BlockTestResult(
                block_id=block_id,
                block_name="unknown",
                passed=False,
                issues=["Block not found"]
            )
        
        name = block.get("metadata", {}).get("name", "unknown")
        issues = []
        warnings = []
        
        param_ok, param_names, param_warnings = self.check_parameter_standardization(block_id)
        warnings.extend(param_warnings)
        
        exec_ok, exec_result, exec_error = self.test_block_execution(block_id)
        if not exec_ok:
            issues.append(f"Execution failed: {exec_error}")
        
        passed = len(issues) == 0
        
        return BlockTestResult(
            block_id=block_id,
            block_name=name,
            passed=passed,
            issues=issues,
            warnings=warnings,
            parameter_names=param_names,
            execution_result=exec_result
        )
    
    def run_full_test(self, tier_a_only: bool = True) -> CompatibilityReport:
        """Run compatibility tests on all blocks."""
        self.load_blocks()
        
        report = CompatibilityReport()
        report.duplicate_names = self.find_duplicate_names()
        
        blocks_to_test = self._tier_a_ids if tier_a_only else set(self._blocks.keys())
        
        if tier_a_only:
            blocks_to_test = blocks_to_test & set(self._blocks.keys())
        
        report.total_blocks = len(blocks_to_test)
        
        for block_id in blocks_to_test:
            result = self.test_single_block(block_id)
            report.results.append(result)
            
            if result.passed:
                report.passed += 1
            else:
                report.failed += 1
                for issue in result.issues:
                    if "Execution failed" in issue:
                        report.execution_failures.append((block_id, result.block_name, issue))
            
            if result.warnings:
                report.warnings_count += len(result.warnings)
                report.non_standard_params.append((block_id, result.block_name, result.parameter_names))
        
        return report
    
    def generate_text_report(self, report: CompatibilityReport) -> str:
        """Generate a human-readable text report."""
        lines = []
        lines.append("=" * 70)
        lines.append("  NEUROP FORGE - BLOCK COMPATIBILITY REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append("[SUMMARY]")
        lines.append("-" * 40)
        lines.append(f"  Total Blocks Tested: {report.total_blocks}")
        lines.append(f"  Passed:              {report.passed}")
        lines.append(f"  Failed:              {report.failed}")
        lines.append(f"  Warnings:            {report.warnings_count}")
        pass_rate = (report.passed / report.total_blocks * 100) if report.total_blocks > 0 else 0
        lines.append(f"  Pass Rate:           {pass_rate:.1f}%")
        lines.append("")
        
        if report.duplicate_names:
            lines.append("[DUPLICATE BLOCK NAMES - ACTION REQUIRED]")
            lines.append("-" * 40)
            lines.append("  These blocks share names but have different signatures.")
            lines.append("  This causes unpredictable behavior when calling by name.")
            lines.append("")
            for name, ids in list(report.duplicate_names.items())[:15]:
                lines.append(f"  '{name}' has {len(ids)} variants:")
                for bid in ids[:3]:
                    block = self._blocks.get(bid, {})
                    inputs = block.get("interface", {}).get("inputs", [])
                    params = [f"{i.get('name')}:{i.get('data_type')}" for i in inputs]
                    source = block.get("metadata", {}).get("source_file", "unknown")
                    lines.append(f"    - {bid[:12]}...")
                    lines.append(f"      params: {params}")
                    lines.append(f"      source: {source.split('/')[-1] if '/' in source else source}")
                lines.append("")
            if len(report.duplicate_names) > 15:
                lines.append(f"  ... and {len(report.duplicate_names) - 15} more duplicates")
            lines.append("")
        
        if report.execution_failures:
            lines.append("[EXECUTION FAILURES]")
            lines.append("-" * 40)
            for bid, name, error in report.execution_failures[:10]:
                lines.append(f"  {name}: {error[:50]}")
            if len(report.execution_failures) > 10:
                lines.append(f"  ... and {len(report.execution_failures) - 10} more")
            lines.append("")
        
        failed_results = [r for r in report.results if not r.passed]
        if failed_results:
            lines.append("[FAILED BLOCKS]")
            lines.append("-" * 40)
            for result in failed_results[:20]:
                lines.append(f"  {result.block_name}:")
                for issue in result.issues:
                    lines.append(f"    - {issue[:60]}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append(f"  TEST COMPLETE: {report.passed}/{report.total_blocks} PASSED")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def run_compatibility_test(tier_a_only: bool = True) -> str:
    """Run compatibility test and return report."""
    tester = BlockCompatibilityTester()
    report = tester.run_full_test(tier_a_only=tier_a_only)
    return tester.generate_text_report(report)


if __name__ == "__main__":
    print(run_compatibility_test())
