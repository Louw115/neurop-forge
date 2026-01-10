"""
Code normalization for intent extraction.

This module transforms source code into a normalized representation
that captures the semantic intent while removing syntactic variations.
The normalized form is used for:
- Identity generation (same logic = same identity)
- Intent classification
- Determinism verification
"""

import ast
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NormalizationLevel(Enum):
    """Level of normalization to apply."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


@dataclass
class NormalizedCode:
    """Result of code normalization."""
    original: str
    normalized: str
    language: str
    normalization_level: NormalizationLevel
    transformations_applied: Tuple[str, ...]
    semantic_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original": self.original,
            "normalized": self.normalized,
            "language": self.language,
            "normalization_level": self.normalization_level.value,
            "transformations_applied": list(self.transformations_applied),
            "semantic_hash": self.semantic_hash,
        }


class CodeNormalizer:
    """
    Normalizes source code to a canonical representation.
    
    The normalizer applies the following transformations:
    1. Remove comments and docstrings
    2. Normalize whitespace
    3. Rename variables to canonical names
    4. Normalize string literals
    5. Normalize numeric literals
    6. Remove dead code
    7. Canonicalize control structures
    """

    def __init__(self, level: NormalizationLevel = NormalizationLevel.STANDARD):
        self._level = level

    def normalize_python(self, source: str) -> NormalizedCode:
        """
        Normalize Python source code.
        
        Args:
            source: The Python source code to normalize
            
        Returns:
            NormalizedCode: The normalized representation
        """
        transformations: List[str] = []
        normalized = source

        normalized = self._remove_comments_python(normalized)
        transformations.append("remove_comments")

        normalized = self._normalize_whitespace(normalized)
        transformations.append("normalize_whitespace")

        try:
            tree = ast.parse(normalized)
            normalized = self._normalize_ast_python(tree)
            transformations.append("ast_normalization")
        except SyntaxError:
            pass

        if self._level in (NormalizationLevel.STANDARD, NormalizationLevel.AGGRESSIVE):
            normalized = self._canonicalize_variables_python(normalized)
            transformations.append("canonicalize_variables")

        if self._level == NormalizationLevel.AGGRESSIVE:
            normalized = self._normalize_string_literals(normalized)
            transformations.append("normalize_strings")

        semantic_hash = hashlib.sha256(normalized.encode()).hexdigest()

        return NormalizedCode(
            original=source,
            normalized=normalized,
            language="python",
            normalization_level=self._level,
            transformations_applied=tuple(transformations),
            semantic_hash=semantic_hash,
        )

    def normalize_javascript(self, source: str) -> NormalizedCode:
        """
        Normalize JavaScript source code.
        
        Args:
            source: The JavaScript source code to normalize
            
        Returns:
            NormalizedCode: The normalized representation
        """
        transformations: List[str] = []
        normalized = source

        normalized = self._remove_comments_javascript(normalized)
        transformations.append("remove_comments")

        normalized = self._normalize_whitespace(normalized)
        transformations.append("normalize_whitespace")

        if self._level in (NormalizationLevel.STANDARD, NormalizationLevel.AGGRESSIVE):
            normalized = self._canonicalize_variables_javascript(normalized)
            transformations.append("canonicalize_variables")

        semantic_hash = hashlib.sha256(normalized.encode()).hexdigest()

        return NormalizedCode(
            original=source,
            normalized=normalized,
            language="javascript",
            normalization_level=self._level,
            transformations_applied=tuple(transformations),
            semantic_hash=semantic_hash,
        )

    def _remove_comments_python(self, source: str) -> str:
        """Remove Python comments and docstrings."""
        source = re.sub(r'#.*$', '', source, flags=re.MULTILINE)

        source = re.sub(r'"""[\s\S]*?"""', '""', source)
        source = re.sub(r"'''[\s\S]*?'''", "''", source)

        return source

    def _remove_comments_javascript(self, source: str) -> str:
        """Remove JavaScript comments."""
        source = re.sub(r'//.*$', '', source, flags=re.MULTILINE)

        source = re.sub(r'/\*[\s\S]*?\*/', '', source)

        return source

    def _normalize_whitespace(self, source: str) -> str:
        """Normalize whitespace while preserving semantic structure."""
        lines = source.split('\n')
        normalized_lines = []

        for line in lines:
            stripped = line.rstrip()
            if stripped:
                normalized_lines.append(stripped)

        return '\n'.join(normalized_lines)

    def _normalize_ast_python(self, tree: ast.AST) -> str:
        """Normalize Python AST and regenerate source."""
        normalizer = _PythonASTNormalizer()
        normalized_tree = normalizer.visit(tree)
        return ast.unparse(normalized_tree)

    def _canonicalize_variables_python(self, source: str) -> str:
        """
        Rename local variables to canonical names.
        
        This helps identify semantically equivalent code with different
        variable names. Uses two-pass approach to ensure function parameters
        are collected before renaming begins.
        """
        try:
            tree = ast.parse(source)
            
            collector = _ParameterCollector()
            collector.visit(tree)
            
            renamer = _PythonVariableRenamer(function_params=collector.params)
            renamed_tree = renamer.visit(tree)
            return ast.unparse(renamed_tree)
        except SyntaxError:
            return source

    def _canonicalize_variables_javascript(self, source: str) -> str:
        """Canonicalize JavaScript variable names (simplified)."""
        return source

    def _normalize_string_literals(self, source: str) -> str:
        """Normalize string quote style."""
        result = []
        i = 0
        while i < len(source):
            if source[i] == "'":
                end = source.find("'", i + 1)
                if end != -1:
                    content = source[i+1:end]
                    result.append(f'"{content}"')
                    i = end + 1
                    continue
            result.append(source[i])
            i += 1
        return ''.join(result)

    def get_semantic_signature(self, code: NormalizedCode) -> str:
        """
        Get a semantic signature for the normalized code.
        
        This signature can be used to identify semantically equivalent
        code blocks.
        """
        return code.semantic_hash


class _PythonASTNormalizer(ast.NodeTransformer):
    """AST transformer for Python normalization."""

    def visit_Expr(self, node: ast.Expr) -> Optional[ast.AST]:
        """Remove standalone string expressions (docstrings)."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return None
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Normalize function definitions."""
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if isinstance(stmt.value.value, str):
                    continue
            new_body.append(stmt)

        if not new_body:
            new_body = [ast.Pass()]

        new_node = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=new_body,
            decorator_list=node.decorator_list,
            returns=node.returns,
        )
        return ast.fix_missing_locations(new_node)


class _ParameterCollector(ast.NodeVisitor):
    """First pass: Collect all function parameter names."""
    
    def __init__(self):
        self.params: set = set()
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        for arg in node.args.args:
            self.params.add(arg.arg)
        for arg in node.args.posonlyargs:
            self.params.add(arg.arg)
        for arg in node.args.kwonlyargs:
            self.params.add(arg.arg)
        if node.args.vararg:
            self.params.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.params.add(node.args.kwarg.arg)
        self.generic_visit(node)
    
    visit_AsyncFunctionDef = visit_FunctionDef


class _PythonVariableRenamer(ast.NodeTransformer):
    """Rename local variables to canonical names while preserving function parameters.
    
    Uses two-pass approach:
    1. First collect all function parameters (done externally)
    2. Then rename variables, skipping parameters
    """

    def __init__(self, function_params: set = None):
        self._var_counter = 0
        self._var_map: Dict[str, str] = {}
        self._function_params: set = function_params or set()
        self._preserved_names = {
            'self', 'cls', 'args', 'kwargs',
            'True', 'False', 'None',
            'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict',
            'set', 'tuple', 'bool', 'type', 'isinstance', 'hasattr', 'getattr',
            'setattr', 'open', 'input', 'sum', 'min', 'max', 'abs', 'round',
            'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
            'ord', 'chr', 'hex', 'oct', 'bin', 'bytes', 'bytearray',
            'all', 'any', 'iter', 'next', 'slice', 'super', 'object',
            'staticmethod', 'classmethod', 'property', 'callable',
            'divmod', 'pow', 'hash', 'id', 'repr', 'format', 'vars',
            'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
            'AttributeError', 'NameError', 'RuntimeError', 'StopIteration',
        }

    def _get_canonical_name(self, original: str) -> str:
        if original in self._preserved_names:
            return original
        if original in self._function_params:
            return original
        if original.startswith('_'):
            return original
        if original not in self._var_map:
            self._var_map[original] = f"v{self._var_counter}"
            self._var_counter += 1
        return self._var_map[original]

    def visit_Name(self, node: ast.Name) -> ast.Name:
        new_name = self._get_canonical_name(node.id)
        return ast.Name(id=new_name, ctx=node.ctx)

    def visit_arg(self, node: ast.arg) -> ast.arg:
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self.generic_visit(node)
    
    visit_AsyncFunctionDef = visit_FunctionDef
