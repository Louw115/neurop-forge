"""
JavaScript parser for extracting code structure and semantics.

This module provides analysis of JavaScript source code to extract
functions and their properties for conversion to NeuropBlocks.
Uses regex-based parsing for core functionality without external dependencies.
"""

import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class JSFunctionType(Enum):
    """Type of JavaScript function."""
    FUNCTION_DECLARATION = "function_declaration"
    FUNCTION_EXPRESSION = "function_expression"
    ARROW_FUNCTION = "arrow_function"
    METHOD = "method"
    ASYNC_FUNCTION = "async_function"


class JSPurity(Enum):
    """Detected purity level of a JavaScript function."""
    PURE = "pure"
    IMPURE = "impure"
    UNKNOWN = "unknown"


class JSSideEffect(Enum):
    """Types of side effects in JavaScript."""
    NONE = "none"
    CONSOLE = "console"
    DOM = "dom"
    FETCH = "fetch"
    STORAGE = "storage"
    GLOBAL_MUTATION = "global_mutation"
    RANDOM = "random"
    DATE = "date"


@dataclass
class JSParameter:
    """Represents a JavaScript function parameter."""
    name: str
    has_default: bool
    default_value: Optional[str]
    is_rest: bool
    position: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "has_default": self.has_default,
            "default_value": self.default_value,
            "is_rest": self.is_rest,
            "position": self.position,
        }


@dataclass
class JSFunction:
    """Represents a parsed JavaScript function."""
    name: str
    source: str
    function_type: JSFunctionType
    parameters: List[JSParameter]
    is_async: bool
    is_generator: bool
    is_exported: bool
    jsdoc: Optional[str]
    purity: JSPurity
    side_effects: Set[JSSideEffect]
    external_calls: Set[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "function_type": self.function_type.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "is_async": self.is_async,
            "is_generator": self.is_generator,
            "is_exported": self.is_exported,
            "jsdoc": self.jsdoc,
            "purity": self.purity.value,
            "side_effects": [s.value for s in self.side_effects],
            "external_calls": list(self.external_calls),
        }

    def get_hash(self) -> str:
        """Get a hash of the function source."""
        return hashlib.sha256(self.source.encode()).hexdigest()


class JavaScriptParser:
    """
    Parser for extracting semantic information from JavaScript source code.
    
    Uses regex-based parsing to analyze:
    - Function declarations and expressions
    - Arrow functions
    - Async functions
    - Side effects and purity
    """

    FUNCTION_PATTERN = re.compile(
        r'(?:export\s+)?(?:async\s+)?function\s*(\*?)\s*(\w+)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )

    ARROW_FUNCTION_PATTERN = re.compile(
        r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>\s*(?:\{|[^{])',
        re.MULTILINE
    )

    METHOD_PATTERN = re.compile(
        r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )

    IMPURE_PATTERNS: Dict[str, JSSideEffect] = {
        r'console\.\w+': JSSideEffect.CONSOLE,
        r'document\.': JSSideEffect.DOM,
        r'window\.': JSSideEffect.DOM,
        r'fetch\(': JSSideEffect.FETCH,
        r'XMLHttpRequest': JSSideEffect.FETCH,
        r'localStorage\.': JSSideEffect.STORAGE,
        r'sessionStorage\.': JSSideEffect.STORAGE,
        r'Math\.random': JSSideEffect.RANDOM,
        r'new\s+Date': JSSideEffect.DATE,
        r'Date\.now': JSSideEffect.DATE,
    }

    def __init__(self):
        self._source = ""

    def parse(self, source: str) -> List[JSFunction]:
        """
        Parse JavaScript source code and extract functions.
        
        Args:
            source: The JavaScript source code
            
        Returns:
            List of parsed functions
        """
        self._source = source
        functions: List[JSFunction] = []

        for match in self.FUNCTION_PATTERN.finditer(source):
            is_generator = match.group(1) == '*'
            name = match.group(2)
            params_str = match.group(3)
            
            func_source = self._extract_function_body(source, match.start())
            is_async = 'async' in source[max(0, match.start()-10):match.start()]
            is_exported = 'export' in source[max(0, match.start()-10):match.start()]
            
            parameters = self._parse_parameters(params_str)
            side_effects, external_calls = self._analyze_side_effects(func_source)
            purity = self._determine_purity(side_effects)
            jsdoc = self._extract_jsdoc(source, match.start())

            functions.append(JSFunction(
                name=name,
                source=func_source,
                function_type=JSFunctionType.FUNCTION_DECLARATION,
                parameters=parameters,
                is_async=is_async,
                is_generator=is_generator,
                is_exported=is_exported,
                jsdoc=jsdoc,
                purity=purity,
                side_effects=side_effects,
                external_calls=external_calls,
            ))

        for match in self.ARROW_FUNCTION_PATTERN.finditer(source):
            name = match.group(1)
            params_str = match.group(2)
            
            if any(f.name == name for f in functions):
                continue
            
            func_source = self._extract_arrow_body(source, match.start())
            is_async = 'async' in source[max(0, match.start()-10):match.end()]
            is_exported = 'export' in source[max(0, match.start()-10):match.start()]
            
            parameters = self._parse_parameters(params_str)
            side_effects, external_calls = self._analyze_side_effects(func_source)
            purity = self._determine_purity(side_effects)
            jsdoc = self._extract_jsdoc(source, match.start())

            functions.append(JSFunction(
                name=name,
                source=func_source,
                function_type=JSFunctionType.ARROW_FUNCTION,
                parameters=parameters,
                is_async=is_async,
                is_generator=False,
                is_exported=is_exported,
                jsdoc=jsdoc,
                purity=purity,
                side_effects=side_effects,
                external_calls=external_calls,
            ))

        return functions

    def _parse_parameters(self, params_str: str) -> List[JSParameter]:
        """Parse function parameters from string."""
        parameters: List[JSParameter] = []
        
        if not params_str.strip():
            return parameters

        params = [p.strip() for p in params_str.split(',')]
        
        for i, param in enumerate(params):
            if not param:
                continue
                
            is_rest = param.startswith('...')
            if is_rest:
                param = param[3:]
            
            has_default = '=' in param
            default_value = None
            name = param
            
            if has_default:
                parts = param.split('=', 1)
                name = parts[0].strip()
                default_value = parts[1].strip()

            parameters.append(JSParameter(
                name=name,
                has_default=has_default,
                default_value=default_value,
                is_rest=is_rest,
                position=i,
            ))

        return parameters

    def _extract_function_body(self, source: str, start: int) -> str:
        """Extract the complete function body including braces."""
        brace_start = source.find('{', start)
        if brace_start == -1:
            return ""

        depth = 0
        end = brace_start
        
        for i, char in enumerate(source[brace_start:], brace_start):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        func_start = start
        while func_start > 0 and source[func_start-1] not in '\n;':
            func_start -= 1

        return source[func_start:end].strip()

    def _extract_arrow_body(self, source: str, start: int) -> str:
        """Extract arrow function body."""
        arrow_pos = source.find('=>', start)
        if arrow_pos == -1:
            return ""

        after_arrow = source[arrow_pos + 2:].lstrip()
        
        if after_arrow.startswith('{'):
            return self._extract_function_body(source, arrow_pos)
        else:
            end = arrow_pos + 2
            for i, char in enumerate(source[arrow_pos + 2:], arrow_pos + 2):
                if char in ';\n' or (char == ',' and self._is_at_top_level(source, start, i)):
                    end = i
                    break
                end = i + 1

            func_start = start
            while func_start > 0 and source[func_start-1] not in '\n;':
                func_start -= 1

            return source[func_start:end].strip()

    def _is_at_top_level(self, source: str, start: int, pos: int) -> bool:
        """Check if position is at top level (not inside braces/parens)."""
        depth = 0
        for char in source[start:pos]:
            if char in '({[':
                depth += 1
            elif char in ')}]':
                depth -= 1
        return depth == 0

    def _extract_jsdoc(self, source: str, func_start: int) -> Optional[str]:
        """Extract JSDoc comment before function."""
        before = source[:func_start].rstrip()
        
        if before.endswith('*/'):
            comment_end = len(before)
            comment_start = before.rfind('/**')
            if comment_start != -1:
                return before[comment_start:comment_end]
        
        return None

    def _analyze_side_effects(
        self,
        source: str,
    ) -> Tuple[Set[JSSideEffect], Set[str]]:
        """Analyze function source for side effects."""
        side_effects: Set[JSSideEffect] = set()
        external_calls: Set[str] = set()

        for pattern, effect in self.IMPURE_PATTERNS.items():
            if re.search(pattern, source):
                side_effects.add(effect)

        call_pattern = re.compile(r'(\w+(?:\.\w+)*)\s*\(')
        for match in call_pattern.finditer(source):
            call_name = match.group(1)
            if call_name not in ('if', 'for', 'while', 'switch', 'catch'):
                external_calls.add(call_name)

        if not side_effects:
            side_effects.add(JSSideEffect.NONE)

        return side_effects, external_calls

    def _determine_purity(self, side_effects: Set[JSSideEffect]) -> JSPurity:
        """Determine purity level from side effects."""
        if side_effects == {JSSideEffect.NONE}:
            return JSPurity.PURE

        impure_effects = {
            JSSideEffect.DOM,
            JSSideEffect.FETCH,
            JSSideEffect.STORAGE,
            JSSideEffect.RANDOM,
            JSSideEffect.DATE,
            JSSideEffect.GLOBAL_MUTATION,
        }

        if side_effects & impure_effects:
            return JSPurity.IMPURE

        if side_effects == {JSSideEffect.CONSOLE}:
            return JSPurity.UNKNOWN

        return JSPurity.UNKNOWN
