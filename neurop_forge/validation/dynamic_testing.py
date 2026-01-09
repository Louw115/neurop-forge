"""
Dynamic testing for NeuropBlock validation.

This module performs runtime testing to verify:
- Deterministic replay (same inputs = same outputs)
- Edge case handling
- Error condition handling
- Performance characteristics
"""

import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import ast


class TestStatus(Enum):
    """Status of a test run."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class TestCase:
    """A test case for dynamic testing."""
    name: str
    inputs: Dict[str, Any]
    expected_output: Optional[Any]
    expected_exception: Optional[str]
    timeout_ms: int = 1000

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": self.inputs,
            "expected_output": self.expected_output,
            "expected_exception": self.expected_exception,
            "timeout_ms": self.timeout_ms,
        }


@dataclass
class TestRun:
    """Result of a single test run."""
    test_case: TestCase
    status: TestStatus
    actual_output: Optional[Any]
    actual_exception: Optional[str]
    execution_time_ms: float
    output_hash: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_case": self.test_case.to_dict(),
            "status": self.status.value,
            "actual_output": str(self.actual_output) if self.actual_output else None,
            "actual_exception": self.actual_exception,
            "execution_time_ms": self.execution_time_ms,
            "output_hash": self.output_hash,
        }


@dataclass
class TestResult:
    """Complete result of dynamic testing."""
    block_identity: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    test_runs: Tuple[TestRun, ...]
    determinism_verified: bool
    coverage_score: float
    total_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "skipped": self.skipped,
            "test_runs": [r.to_dict() for r in self.test_runs],
            "determinism_verified": self.determinism_verified,
            "coverage_score": self.coverage_score,
            "total_time_ms": self.total_time_ms,
        }

    def is_passing(self) -> bool:
        """Check if all tests passed."""
        return self.failed == 0 and self.errors == 0


class DynamicTester:
    """
    Dynamic tester for NeuropBlock validation.
    
    Performs:
    - Deterministic replay testing
    - Edge case testing
    - Type boundary testing
    - Exception handling verification
    """

    DEFAULT_EDGE_CASES: Dict[str, List[Any]] = {
        "integer": [0, 1, -1, 2**31 - 1, -(2**31)],
        "float": [0.0, 1.0, -1.0, float('inf'), float('-inf')],
        "string": ["", " ", "a", "hello world", "\n\t"],
        "list": [[], [1], [1, 2, 3], list(range(100))],
        "boolean": [True, False],
    }

    def __init__(self, max_execution_time_ms: int = 5000):
        self._max_execution_time_ms = max_execution_time_ms

    def test_block(
        self,
        block: Any,
        test_cases: Optional[List[TestCase]] = None,
        verify_determinism: bool = True,
    ) -> TestResult:
        """
        Run dynamic tests on a NeuropBlock.
        
        Args:
            block: The NeuropBlock to test
            test_cases: Optional list of test cases
            verify_determinism: Whether to verify determinism
            
        Returns:
            TestResult with all findings
        """
        start_time = time.time()

        block_identity = block.get_identity_hash()

        if test_cases is None:
            test_cases = self._generate_test_cases(block)

        test_runs: List[TestRun] = []
        passed = 0
        failed = 0
        errors = 0
        skipped = 0

        executable = self._compile_block(block)

        if executable is None:
            return TestResult(
                block_identity=block_identity,
                total_tests=len(test_cases),
                passed=0,
                failed=0,
                errors=len(test_cases),
                skipped=0,
                test_runs=(),
                determinism_verified=False,
                coverage_score=0.0,
                total_time_ms=(time.time() - start_time) * 1000,
            )

        for test_case in test_cases:
            run = self._execute_test(executable, test_case, block)
            test_runs.append(run)

            if run.status == TestStatus.PASSED:
                passed += 1
            elif run.status == TestStatus.FAILED:
                failed += 1
            elif run.status == TestStatus.ERROR:
                errors += 1
            else:
                skipped += 1

        determinism_verified = False
        if verify_determinism and block.constraints.deterministic:
            determinism_verified = self._verify_determinism(
                executable, test_cases, block
            )

        coverage_score = passed / max(len(test_cases), 1)

        return TestResult(
            block_identity=block_identity,
            total_tests=len(test_cases),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            test_runs=tuple(test_runs),
            determinism_verified=determinism_verified,
            coverage_score=coverage_score,
            total_time_ms=(time.time() - start_time) * 1000,
        )

    def _generate_test_cases(self, block: Any) -> List[TestCase]:
        """Generate test cases from block interface."""
        test_cases: List[TestCase] = []

        interface = block.interface
        category = block.metadata.category

        if category == "arithmetic":
            test_cases.extend(self._generate_arithmetic_tests(interface))
        elif category == "string":
            test_cases.extend(self._generate_string_tests(interface))
        elif category == "collection":
            test_cases.extend(self._generate_collection_tests(interface))
        else:
            test_cases.extend(self._generate_generic_tests(interface))

        return test_cases

    def _generate_arithmetic_tests(self, interface: Any) -> List[TestCase]:
        """Generate test cases for arithmetic blocks."""
        tests: List[TestCase] = []
        param_names = [p.name for p in interface.inputs]

        if len(param_names) == 2:
            test_inputs = [
                {"a": 1, "b": 2},
                {"a": 0, "b": 0},
                {"a": -1, "b": 1},
                {"a": 100, "b": 50},
                {"a": 0.5, "b": 0.5},
            ]

            for i, inputs in enumerate(test_inputs):
                mapped_inputs = {}
                for j, name in enumerate(param_names[:2]):
                    key = list(inputs.keys())[j]
                    mapped_inputs[name] = inputs[key]

                tests.append(TestCase(
                    name=f"arithmetic_test_{i}",
                    inputs=mapped_inputs,
                    expected_output=None,
                    expected_exception=None,
                ))

        elif len(param_names) == 1:
            test_values = [0, 1, -1, 10, 100, 0.5, -0.5]
            for i, val in enumerate(test_values):
                tests.append(TestCase(
                    name=f"unary_test_{i}",
                    inputs={param_names[0]: val},
                    expected_output=None,
                    expected_exception=None,
                ))

        return tests

    def _generate_string_tests(self, interface: Any) -> List[TestCase]:
        """Generate test cases for string blocks."""
        tests: List[TestCase] = []
        param_names = [p.name for p in interface.inputs]

        if param_names:
            first_param = param_names[0]
            test_values = ["", "hello", "Hello World", " spaces ", "123", "\n\t"]

            for i, val in enumerate(test_values):
                inputs = {first_param: val}
                for name in param_names[1:]:
                    inputs[name] = "default"

                tests.append(TestCase(
                    name=f"string_test_{i}",
                    inputs=inputs,
                    expected_output=None,
                    expected_exception=None,
                ))

        return tests

    def _generate_collection_tests(self, interface: Any) -> List[TestCase]:
        """Generate test cases for collection blocks."""
        tests: List[TestCase] = []
        param_names = [p.name for p in interface.inputs]

        if param_names:
            first_param = param_names[0]
            test_values = [[], [1], [1, 2, 3], list(range(10)), ["a", "b", "c"]]

            for i, val in enumerate(test_values):
                inputs = {first_param: val}
                for name in param_names[1:]:
                    inputs[name] = 0

                tests.append(TestCase(
                    name=f"collection_test_{i}",
                    inputs=inputs,
                    expected_output=None,
                    expected_exception=None,
                ))

        return tests

    def _generate_generic_tests(self, interface: Any) -> List[TestCase]:
        """Generate generic test cases."""
        tests: List[TestCase] = []
        param_names = [p.name for p in interface.inputs]

        if param_names:
            inputs = {name: None for name in param_names}
            tests.append(TestCase(
                name="null_input_test",
                inputs=inputs,
                expected_output=None,
                expected_exception="Exception",
            ))

        return tests

    def _compile_block(self, block: Any) -> Optional[Callable]:
        """Compile block logic into an executable function."""
        logic = block.logic
        language = block.metadata.language

        if language != "python":
            return None

        try:
            tree = ast.parse(logic)

            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    break

            if func_def is None:
                return None

            local_ns: Dict[str, Any] = {}
            exec(compile(tree, "<block>", "exec"), local_ns)

            return local_ns.get(func_def.name)

        except Exception:
            return None

    def _execute_test(
        self,
        executable: Callable,
        test_case: TestCase,
        block: Any,
    ) -> TestRun:
        """Execute a single test case."""
        start_time = time.time()

        try:
            result = executable(**test_case.inputs)
            execution_time = (time.time() - start_time) * 1000

            output_hash = hashlib.sha256(
                str(result).encode()
            ).hexdigest()

            if test_case.expected_exception:
                return TestRun(
                    test_case=test_case,
                    status=TestStatus.FAILED,
                    actual_output=result,
                    actual_exception=None,
                    execution_time_ms=execution_time,
                    output_hash=output_hash,
                )

            if test_case.expected_output is not None:
                if result == test_case.expected_output:
                    status = TestStatus.PASSED
                else:
                    status = TestStatus.FAILED
            else:
                status = TestStatus.PASSED

            return TestRun(
                test_case=test_case,
                status=status,
                actual_output=result,
                actual_exception=None,
                execution_time_ms=execution_time,
                output_hash=output_hash,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            exception_name = type(e).__name__

            if test_case.expected_exception:
                if test_case.expected_exception in exception_name or test_case.expected_exception == "Exception":
                    status = TestStatus.PASSED
                else:
                    status = TestStatus.FAILED
            else:
                status = TestStatus.ERROR

            return TestRun(
                test_case=test_case,
                status=status,
                actual_output=None,
                actual_exception=f"{exception_name}: {e}",
                execution_time_ms=execution_time,
                output_hash=None,
            )

    def _verify_determinism(
        self,
        executable: Callable,
        test_cases: List[TestCase],
        block: Any,
        iterations: int = 3,
    ) -> bool:
        """Verify that the block is deterministic."""
        for test_case in test_cases:
            hashes: List[str] = []

            for _ in range(iterations):
                try:
                    result = executable(**test_case.inputs)
                    result_hash = hashlib.sha256(str(result).encode()).hexdigest()
                    hashes.append(result_hash)
                except Exception:
                    hashes.append("exception")

            if len(set(hashes)) > 1:
                return False

        return True
