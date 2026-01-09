"""
Static analysis for NeuropBlock validation.

This module performs static analysis on blocks to verify:
- Forbidden operations are not present
- Purity claims are accurate
- Determinism claims are accurate
- No hidden I/O operations
- No implicit state
"""

import ast
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import NeuropBlock, PurityLevel, IOType


class ViolationType(Enum):
    """Types of static analysis violations."""
    FORBIDDEN_OPERATION = "forbidden_operation"
    PURITY_VIOLATION = "purity_violation"
    DETERMINISM_VIOLATION = "determinism_violation"
    HIDDEN_IO = "hidden_io"
    IMPLICIT_STATE = "implicit_state"
    UNSAFE_CONSTRUCT = "unsafe_construct"
    COMPLEXITY_EXCEEDED = "complexity_exceeded"


class Severity(Enum):
    """Severity of violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Violation:
    """A static analysis violation."""
    violation_type: ViolationType
    severity: Severity
    message: str
    location: Optional[str]
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "evidence": self.evidence,
        }


@dataclass
class AnalysisResult:
    """Result of static analysis."""
    passed: bool
    violations: Tuple[Violation, ...]
    warnings: Tuple[str, ...]
    metrics: Dict[str, Any]
    analyzed_lines: int
    analysis_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": list(self.warnings),
            "metrics": self.metrics,
            "analyzed_lines": self.analyzed_lines,
            "analysis_time_ms": self.analysis_time_ms,
        }

    def get_critical_violations(self) -> List[Violation]:
        """Get only critical violations."""
        return [v for v in self.violations if v.severity == Severity.CRITICAL]


class StaticAnalyzer:
    """
    Static analyzer for NeuropBlock validation.
    
    Enforces:
    - No forbidden operations (exec, eval, compile, __import__)
    - Purity is accurately declared
    - Determinism is accurately declared
    - No hidden I/O operations
    - No implicit state access
    """

    FORBIDDEN_FUNCTIONS: Set[str] = {
        "exec", "eval", "compile", "__import__", "importlib.import_module",
        "open", "input", "print",
        "os.system", "subprocess.run", "subprocess.call", "subprocess.Popen",
        "socket", "urllib", "requests.get", "requests.post",
        "getattr", "setattr", "delattr",
    }

    FORBIDDEN_FOR_PURE: Set[str] = {
        "print", "open", "write", "read",
        "random", "randint", "choice", "shuffle",
        "time", "sleep", "datetime.now", "datetime.today",
        "os.environ", "os.getenv",
    }

    NON_DETERMINISTIC_FUNCTIONS: Set[str] = {
        "random", "randint", "choice", "shuffle", "sample",
        "uuid", "uuid4", "uuid1",
        "time", "datetime.now", "datetime.today", "datetime.utcnow",
        "os.urandom", "secrets",
    }

    GLOBAL_STATE_PATTERNS: List[re.Pattern] = [
        re.compile(r'\bglobal\s+\w+'),
        re.compile(r'\bos\.environ'),
        re.compile(r'\bsys\.'),
    ]

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode

    def analyze(self, block: NeuropBlock) -> AnalysisResult:
        """
        Perform static analysis on a NeuropBlock.
        
        Args:
            block: The block to analyze
            
        Returns:
            AnalysisResult with findings
        """
        import time
        start_time = time.time()

        violations: List[Violation] = []
        warnings: List[str] = []
        metrics: Dict[str, Any] = {}

        logic = block.logic
        lines = logic.split('\n')
        metrics["line_count"] = len(lines)

        if block.metadata.language == "python":
            try:
                tree = ast.parse(logic)
                violations.extend(self._analyze_python_ast(tree, block))
                metrics["ast_nodes"] = sum(1 for _ in ast.walk(tree))
            except SyntaxError as e:
                violations.append(Violation(
                    violation_type=ViolationType.UNSAFE_CONSTRUCT,
                    severity=Severity.CRITICAL,
                    message=f"Invalid Python syntax: {e}",
                    location=f"line {e.lineno}",
                    evidence=str(e),
                ))
        else:
            violations.extend(self._analyze_javascript(logic, block))

        violations.extend(self._check_forbidden_patterns(logic))

        if block.constraints.purity == PurityLevel.PURE:
            violations.extend(self._verify_purity(logic, block))

        if block.constraints.deterministic:
            violations.extend(self._verify_determinism(logic, block))

        violations.extend(self._check_hidden_io(logic, block))

        violations.extend(self._check_implicit_state(logic))

        complexity = self._calculate_complexity(logic)
        metrics["cyclomatic_complexity"] = complexity
        if complexity > 10:
            warnings.append(f"High cyclomatic complexity: {complexity}")

        passed = all(v.severity != Severity.CRITICAL for v in violations)

        return AnalysisResult(
            passed=passed,
            violations=tuple(violations),
            warnings=tuple(warnings),
            metrics=metrics,
            analyzed_lines=len(lines),
            analysis_time_ms=(time.time() - start_time) * 1000,
        )

    def _analyze_python_ast(
        self,
        tree: ast.AST,
        block: NeuropBlock,
    ) -> List[Violation]:
        """Analyze Python AST for violations."""
        violations: List[Violation] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name and func_name in self.FORBIDDEN_FUNCTIONS:
                    violations.append(Violation(
                        violation_type=ViolationType.FORBIDDEN_OPERATION,
                        severity=Severity.CRITICAL,
                        message=f"Forbidden function call: {func_name}",
                        location=f"line {node.lineno}" if hasattr(node, 'lineno') else None,
                        evidence=ast.unparse(node),
                    ))

            elif isinstance(node, ast.Global):
                violations.append(Violation(
                    violation_type=ViolationType.IMPLICIT_STATE,
                    severity=Severity.HIGH,
                    message=f"Global statement: {', '.join(node.names)}",
                    location=f"line {node.lineno}" if hasattr(node, 'lineno') else None,
                    evidence=f"global {', '.join(node.names)}",
                ))

            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                violations.append(Violation(
                    violation_type=ViolationType.UNSAFE_CONSTRUCT,
                    severity=Severity.MEDIUM,
                    message="Import statement in block logic",
                    location=f"line {node.lineno}" if hasattr(node, 'lineno') else None,
                    evidence=ast.unparse(node),
                ))

        return violations

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Get the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return None

    def _analyze_javascript(
        self,
        logic: str,
        block: NeuropBlock,
    ) -> List[Violation]:
        """Analyze JavaScript code for violations."""
        violations: List[Violation] = []

        forbidden_patterns = [
            (r'\beval\s*\(', "eval()"),
            (r'\bFunction\s*\(', "Function()"),
            (r'\bfetch\s*\(', "fetch()"),
            (r'\bXMLHttpRequest', "XMLHttpRequest"),
            (r'\blocalStorage\.', "localStorage"),
            (r'\bsessionStorage\.', "sessionStorage"),
            (r'\bdocument\.', "document"),
            (r'\bwindow\.', "window"),
        ]

        for pattern, name in forbidden_patterns:
            if re.search(pattern, logic):
                violations.append(Violation(
                    violation_type=ViolationType.FORBIDDEN_OPERATION,
                    severity=Severity.CRITICAL,
                    message=f"Forbidden operation: {name}",
                    location=None,
                    evidence=name,
                ))

        return violations

    def _check_forbidden_patterns(self, logic: str) -> List[Violation]:
        """Check for forbidden patterns in any language."""
        violations: List[Violation] = []

        for func in self.FORBIDDEN_FUNCTIONS:
            pattern = rf'\b{re.escape(func)}\s*\('
            if re.search(pattern, logic):
                violations.append(Violation(
                    violation_type=ViolationType.FORBIDDEN_OPERATION,
                    severity=Severity.CRITICAL,
                    message=f"Forbidden function: {func}",
                    location=None,
                    evidence=func,
                ))

        return violations

    def _verify_purity(self, logic: str, block: NeuropBlock) -> List[Violation]:
        """Verify purity claims are accurate."""
        violations: List[Violation] = []

        for func in self.FORBIDDEN_FOR_PURE:
            if func in logic:
                violations.append(Violation(
                    violation_type=ViolationType.PURITY_VIOLATION,
                    severity=Severity.HIGH,
                    message=f"Pure block contains impure operation: {func}",
                    location=None,
                    evidence=func,
                ))

        return violations

    def _verify_determinism(self, logic: str, block: NeuropBlock) -> List[Violation]:
        """Verify determinism claims are accurate."""
        violations: List[Violation] = []

        for func in self.NON_DETERMINISTIC_FUNCTIONS:
            if func in logic:
                violations.append(Violation(
                    violation_type=ViolationType.DETERMINISM_VIOLATION,
                    severity=Severity.HIGH,
                    message=f"Deterministic block contains non-deterministic operation: {func}",
                    location=None,
                    evidence=func,
                ))

        return violations

    def _check_hidden_io(self, logic: str, block: NeuropBlock) -> List[Violation]:
        """Check for hidden I/O not declared in constraints."""
        violations: List[Violation] = []

        io_patterns = {
            r'\bopen\s*\(': IOType.FILE_READ,
            r'\.read\s*\(': IOType.FILE_READ,
            r'\.write\s*\(': IOType.FILE_WRITE,
            r'\bfetch\s*\(': IOType.NETWORK_READ,
            r'\brequests\.': IOType.NETWORK_READ,
            r'\bprint\s*\(': IOType.CONSOLE_OUTPUT,
        }

        declared_io = block.constraints.io_operations

        for pattern, io_type in io_patterns.items():
            if re.search(pattern, logic):
                if io_type not in declared_io and IOType.NONE in declared_io:
                    violations.append(Violation(
                        violation_type=ViolationType.HIDDEN_IO,
                        severity=Severity.HIGH,
                        message=f"Hidden I/O operation: {io_type.value}",
                        location=None,
                        evidence=pattern,
                    ))

        return violations

    def _check_implicit_state(self, logic: str) -> List[Violation]:
        """Check for implicit state access."""
        violations: List[Violation] = []

        for pattern in self.GLOBAL_STATE_PATTERNS:
            match = pattern.search(logic)
            if match:
                violations.append(Violation(
                    violation_type=ViolationType.IMPLICIT_STATE,
                    severity=Severity.HIGH,
                    message="Implicit global state access",
                    location=None,
                    evidence=match.group(),
                ))

        return violations

    def _calculate_complexity(self, logic: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1

        branch_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b',
            r'\band\b', r'\bor\b',
            r'\btry\b', r'\bexcept\b',
            r'\?',  # Ternary
        ]

        for pattern in branch_patterns:
            complexity += len(re.findall(pattern, logic))

        return complexity

    def quick_check(self, logic: str, language: str = "python") -> bool:
        """Quick check if logic has any forbidden operations."""
        for func in self.FORBIDDEN_FUNCTIONS:
            if func in logic:
                return False
        return True
