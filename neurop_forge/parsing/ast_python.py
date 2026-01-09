"""
Python AST parser for extracting code structure and semantics.

This module provides deep analysis of Python source code using the AST
to extract functions, classes, and their properties for conversion to
NeuropBlocks.
"""

import ast
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FunctionPurity(Enum):
    """Detected purity level of a function."""
    PURE = "pure"
    IMPURE = "impure"
    UNKNOWN = "unknown"


class SideEffectType(Enum):
    """Types of side effects a function may have."""
    NONE = "none"
    PRINT = "print"
    FILE_IO = "file_io"
    NETWORK = "network"
    GLOBAL_MUTATION = "global_mutation"
    RANDOM = "random"
    TIME = "time"
    EXCEPTION = "exception"


@dataclass
class TypeAnnotation:
    """Represents a type annotation."""
    raw: str
    base_type: str
    is_optional: bool = False
    is_list: bool = False
    is_dict: bool = False
    inner_types: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw": self.raw,
            "base_type": self.base_type,
            "is_optional": self.is_optional,
            "is_list": self.is_list,
            "is_dict": self.is_dict,
            "inner_types": list(self.inner_types),
        }


@dataclass
class FunctionParameter:
    """Represents a function parameter."""
    name: str
    annotation: Optional[TypeAnnotation]
    has_default: bool
    default_value: Optional[str]
    position: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "annotation": self.annotation.to_dict() if self.annotation else None,
            "has_default": self.has_default,
            "default_value": self.default_value,
            "position": self.position,
        }


@dataclass
class PythonFunction:
    """Represents a parsed Python function."""
    name: str
    source: str
    line_start: int
    line_end: int
    parameters: List[FunctionParameter]
    return_annotation: Optional[TypeAnnotation]
    decorators: List[str]
    docstring: Optional[str]
    is_method: bool
    is_static: bool
    is_classmethod: bool
    is_async: bool
    purity: FunctionPurity
    side_effects: Set[SideEffectType]
    calls_external: Set[str]
    global_reads: Set[str]
    global_writes: Set[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_annotation": self.return_annotation.to_dict() if self.return_annotation else None,
            "decorators": self.decorators,
            "docstring": self.docstring,
            "is_method": self.is_method,
            "is_static": self.is_static,
            "is_classmethod": self.is_classmethod,
            "is_async": self.is_async,
            "purity": self.purity.value,
            "side_effects": [s.value for s in self.side_effects],
            "calls_external": list(self.calls_external),
            "global_reads": list(self.global_reads),
            "global_writes": list(self.global_writes),
        }

    def get_hash(self) -> str:
        """Get a hash of the function source."""
        return hashlib.sha256(self.source.encode()).hexdigest()


@dataclass
class PythonClass:
    """Represents a parsed Python class."""
    name: str
    source: str
    line_start: int
    line_end: int
    bases: List[str]
    methods: List[PythonFunction]
    class_variables: Dict[str, Optional[TypeAnnotation]]
    decorators: List[str]
    docstring: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "bases": self.bases,
            "methods": [m.to_dict() for m in self.methods],
            "class_variables": {
                k: v.to_dict() if v else None 
                for k, v in self.class_variables.items()
            },
            "decorators": self.decorators,
            "docstring": self.docstring,
        }


class PythonASTParser:
    """
    Parser for extracting semantic information from Python source code.
    
    Uses the AST module to analyze:
    - Function definitions and their signatures
    - Class definitions and methods
    - Type annotations
    - Side effects and purity
    - External dependencies
    """

    IMPURE_FUNCTIONS: Set[str] = {
        "print", "input", "open", "write", "read",
        "random", "randint", "choice", "shuffle",
        "time", "sleep", "datetime",
        "request", "get", "post", "urlopen",
        "exec", "eval", "compile",
        "os.system", "subprocess.run", "subprocess.call",
    }

    IO_FUNCTIONS: Set[str] = {
        "open", "read", "write", "close",
        "request", "get", "post", "urlopen",
        "socket", "connect", "send", "recv",
    }

    def __init__(self):
        self._source_lines: List[str] = []

    def parse(self, source: str) -> Tuple[List[PythonFunction], List[PythonClass]]:
        """
        Parse Python source code and extract functions and classes.
        
        Args:
            source: The Python source code
            
        Returns:
            Tuple of (functions, classes)
        """
        self._source_lines = source.split('\n')
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

        functions: List[PythonFunction] = []
        classes: List[PythonClass] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                parent = self._find_parent(tree, node)
                if not isinstance(parent, ast.ClassDef):
                    func = self._parse_function(node, source, is_method=False)
                    functions.append(func)

            elif isinstance(node, ast.ClassDef):
                cls = self._parse_class(node, source)
                classes.append(cls)

        return functions, classes

    def parse_functions_only(self, source: str) -> List[PythonFunction]:
        """Parse and return only top-level functions."""
        functions, _ = self.parse(source)
        return functions

    def _find_parent(self, tree: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Find the parent node of a target node."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is target:
                    return node
        return None

    def _parse_function(
        self,
        node: ast.FunctionDef,
        source: str,
        is_method: bool = False,
    ) -> PythonFunction:
        """Parse a function definition node."""
        func_source = self._extract_source(node.lineno, node.end_lineno or node.lineno)

        parameters = self._parse_parameters(node.args)

        return_annotation = None
        if node.returns:
            return_annotation = self._parse_type_annotation(node.returns)

        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        docstring = ast.get_docstring(node)

        is_static = "staticmethod" in decorators
        is_classmethod = "classmethod" in decorators
        is_async = isinstance(node, ast.AsyncFunctionDef)

        side_effects, calls, global_reads, global_writes = self._analyze_side_effects(node)
        purity = self._determine_purity(side_effects, global_reads, global_writes)

        return PythonFunction(
            name=node.name,
            source=func_source,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=parameters,
            return_annotation=return_annotation,
            decorators=decorators,
            docstring=docstring,
            is_method=is_method,
            is_static=is_static,
            is_classmethod=is_classmethod,
            is_async=is_async,
            purity=purity,
            side_effects=side_effects,
            calls_external=calls,
            global_reads=global_reads,
            global_writes=global_writes,
        )

    def _parse_class(self, node: ast.ClassDef, source: str) -> PythonClass:
        """Parse a class definition node."""
        class_source = self._extract_source(node.lineno, node.end_lineno or node.lineno)

        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attribute_name(base)}")

        methods = []
        class_variables: Dict[str, Optional[TypeAnnotation]] = {}

        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method = self._parse_function(item, source, is_method=True)
                methods.append(method)

            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    var_name = item.target.id
                    annotation = self._parse_type_annotation(item.annotation)
                    class_variables[var_name] = annotation

        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        docstring = ast.get_docstring(node)

        return PythonClass(
            name=node.name,
            source=class_source,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            bases=bases,
            methods=methods,
            class_variables=class_variables,
            decorators=decorators,
            docstring=docstring,
        )

    def _parse_parameters(self, args: ast.arguments) -> List[FunctionParameter]:
        """Parse function parameters."""
        parameters = []
        
        defaults_offset = len(args.args) - len(args.defaults)

        for i, arg in enumerate(args.args):
            annotation = None
            if arg.annotation:
                annotation = self._parse_type_annotation(arg.annotation)

            has_default = i >= defaults_offset
            default_value = None
            if has_default:
                default_idx = i - defaults_offset
                default_node = args.defaults[default_idx]
                default_value = ast.unparse(default_node)

            param = FunctionParameter(
                name=arg.arg,
                annotation=annotation,
                has_default=has_default,
                default_value=default_value,
                position=i,
            )
            parameters.append(param)

        return parameters

    def _parse_type_annotation(self, node: ast.AST) -> TypeAnnotation:
        """Parse a type annotation node."""
        raw = ast.unparse(node)

        if isinstance(node, ast.Name):
            return TypeAnnotation(
                raw=raw,
                base_type=node.id,
            )

        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                base = node.value.id
                is_optional = base == "Optional"
                is_list = base in ("List", "list")
                is_dict = base in ("Dict", "dict")

                inner_types = []
                if isinstance(node.slice, ast.Tuple):
                    for elt in node.slice.elts:
                        inner_types.append(ast.unparse(elt))
                else:
                    inner_types.append(ast.unparse(node.slice))

                return TypeAnnotation(
                    raw=raw,
                    base_type=base,
                    is_optional=is_optional,
                    is_list=is_list,
                    is_dict=is_dict,
                    inner_types=tuple(inner_types),
                )

        return TypeAnnotation(raw=raw, base_type=raw)

    def _get_decorator_name(self, node: ast.AST) -> str:
        """Get the name of a decorator."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ast.unparse(node)

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full dotted name of an attribute."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _extract_source(self, start_line: int, end_line: int) -> str:
        """Extract source code lines."""
        return '\n'.join(self._source_lines[start_line - 1:end_line])

    def _analyze_side_effects(
        self,
        node: ast.FunctionDef,
    ) -> Tuple[Set[SideEffectType], Set[str], Set[str], Set[str]]:
        """Analyze a function for side effects."""
        side_effects: Set[SideEffectType] = set()
        external_calls: Set[str] = set()
        global_reads: Set[str] = set()
        global_writes: Set[str] = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Global):
                for name in child.names:
                    global_writes.add(name)
                side_effects.add(SideEffectType.GLOBAL_MUTATION)

            elif isinstance(child, ast.Call):
                call_name = self._get_call_name(child)
                if call_name:
                    external_calls.add(call_name)

                    if call_name in ("print", "logging"):
                        side_effects.add(SideEffectType.PRINT)
                    elif call_name in self.IO_FUNCTIONS:
                        side_effects.add(SideEffectType.FILE_IO)
                    elif "random" in call_name.lower():
                        side_effects.add(SideEffectType.RANDOM)
                    elif "time" in call_name.lower() or "datetime" in call_name.lower():
                        side_effects.add(SideEffectType.TIME)

            elif isinstance(child, ast.Raise):
                side_effects.add(SideEffectType.EXCEPTION)

        if not side_effects:
            side_effects.add(SideEffectType.NONE)

        return side_effects, external_calls, global_reads, global_writes

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Get the name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return self._get_attribute_name(node.func)
        return None

    def _determine_purity(
        self,
        side_effects: Set[SideEffectType],
        global_reads: Set[str],
        global_writes: Set[str],
    ) -> FunctionPurity:
        """Determine the purity level of a function."""
        if side_effects == {SideEffectType.NONE} and not global_reads and not global_writes:
            return FunctionPurity.PURE

        if global_writes or SideEffectType.GLOBAL_MUTATION in side_effects:
            return FunctionPurity.IMPURE

        impure_effects = {
            SideEffectType.FILE_IO,
            SideEffectType.NETWORK,
            SideEffectType.RANDOM,
            SideEffectType.TIME,
        }

        if side_effects & impure_effects:
            return FunctionPurity.IMPURE

        if side_effects == {SideEffectType.EXCEPTION} or side_effects == {SideEffectType.PRINT, SideEffectType.NONE}:
            return FunctionPurity.UNKNOWN

        return FunctionPurity.UNKNOWN
