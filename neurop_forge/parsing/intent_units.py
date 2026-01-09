"""
Intent unit extraction from parsed code.

This module extracts atomic intent units from parsed functions and classes.
An intent unit represents a single, well-defined purpose that can be
converted into a NeuropBlock.
"""

import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from neurop_forge.parsing.ast_python import PythonFunction, PythonClass, FunctionPurity
from neurop_forge.parsing.ast_javascript import JSFunction, JSPurity


class IntentCategory(Enum):
    """Categories of atomic intents."""
    ARITHMETIC = "arithmetic"
    STRING_MANIPULATION = "string_manipulation"
    LIST_OPERATION = "list_operation"
    DICT_OPERATION = "dict_operation"
    COMPARISON = "comparison"
    CONVERSION = "conversion"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    SORTING = "sorting"
    SEARCHING = "searching"
    IO_OPERATION = "io_operation"
    UTILITY = "utility"
    UNKNOWN = "unknown"


class AtomicityLevel(Enum):
    """How atomic (single-purpose) a unit is."""
    ATOMIC = "atomic"
    COMPOSITE = "composite"
    COMPLEX = "complex"


@dataclass
class AtomicIntent:
    """
    Represents an atomic intent extracted from code.
    
    An atomic intent is a single, well-defined purpose:
    - One clear action or computation
    - No mixed responsibilities
    - Verifiable behavior
    """
    intent_id: str
    name: str
    description: str
    category: IntentCategory
    atomicity: AtomicityLevel
    keywords: Tuple[str, ...]
    semantic_signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "atomicity": self.atomicity.value,
            "keywords": list(self.keywords),
            "semantic_signature": self.semantic_signature,
        }


@dataclass
class IntentUnit:
    """
    A code unit with its extracted atomic intent.
    
    This is the intermediate representation between raw code
    and a NeuropBlock.
    """
    source: str
    language: str
    function_name: str
    intent: AtomicIntent
    is_pure: bool
    is_deterministic: bool
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    side_effects: List[str]
    dependencies: List[str]
    source_location: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "language": self.language,
            "function_name": self.function_name,
            "intent": self.intent.to_dict(),
            "is_pure": self.is_pure,
            "is_deterministic": self.is_deterministic,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "side_effects": self.side_effects,
            "dependencies": self.dependencies,
            "source_location": self.source_location,
        }

    def get_hash(self) -> str:
        """Get a hash of this intent unit."""
        content = f"{self.source}:{self.intent.intent_id}"
        return hashlib.sha256(content.encode()).hexdigest()


class IntentExtractor:
    """
    Extracts atomic intent units from parsed code structures.
    
    The extractor analyzes function names, docstrings, parameters,
    and logic patterns to determine the atomic intent of each unit.
    """

    ARITHMETIC_KEYWORDS = {
        "add", "subtract", "multiply", "divide", "sum", "product",
        "increment", "decrement", "modulo", "power", "sqrt", "abs",
        "floor", "ceil", "round", "min", "max", "average", "mean",
        "calculate", "compute",
    }

    STRING_KEYWORDS = {
        "concat", "join", "split", "trim", "strip", "upper", "lower",
        "capitalize", "replace", "format", "parse", "substring", "slice",
        "pad", "reverse", "encode", "decode",
    }

    LIST_KEYWORDS = {
        "append", "extend", "insert", "remove", "pop", "push", "shift",
        "unshift", "slice", "splice", "concat", "flatten", "unique",
        "dedupe", "chunk", "partition",
    }

    COMPARISON_KEYWORDS = {
        "compare", "equal", "equals", "match", "diff", "greater", "less",
        "between", "contains", "includes", "starts", "ends",
    }

    VALIDATION_KEYWORDS = {
        "validate", "check", "verify", "is_valid", "assert", "ensure",
        "confirm", "test", "is_", "has_",
    }

    TRANSFORMATION_KEYWORDS = {
        "transform", "convert", "map", "to_", "from_", "parse", "serialize",
        "deserialize", "encode", "decode", "format",
    }

    AGGREGATION_KEYWORDS = {
        "sum", "count", "total", "aggregate", "reduce", "fold", "accumulate",
        "collect", "gather", "combine", "merge",
    }

    FILTER_KEYWORDS = {
        "filter", "select", "where", "find", "search", "query", "get",
        "fetch", "lookup", "pick", "reject", "exclude",
    }

    SORT_KEYWORDS = {
        "sort", "order", "rank", "arrange", "organize", "group",
    }

    def __init__(self):
        self._intent_counter = 0

    def extract_from_python_function(
        self,
        func: PythonFunction,
        source_file: Optional[str] = None,
    ) -> IntentUnit:
        """
        Extract intent unit from a Python function.
        
        Args:
            func: The parsed Python function
            source_file: Optional source file path
            
        Returns:
            IntentUnit: The extracted intent unit
        """
        intent = self._classify_intent(
            func.name,
            func.docstring or "",
            set(p.name for p in func.parameters),
        )

        is_pure = func.purity == FunctionPurity.PURE
        is_deterministic = is_pure  # Pure functions are deterministic

        parameters = [
            {
                "name": p.name,
                "type": p.annotation.raw if p.annotation else None,
                "optional": p.has_default,
                "default": p.default_value,
            }
            for p in func.parameters
        ]

        return_type = func.return_annotation.raw if func.return_annotation else None

        side_effects = [se.value for se in func.side_effects if se.value != "none"]

        dependencies = list(func.calls_external)

        source_location = None
        if source_file:
            source_location = {
                "file": source_file,
                "line_start": func.line_start,
                "line_end": func.line_end,
            }

        return IntentUnit(
            source=func.source,
            language="python",
            function_name=func.name,
            intent=intent,
            is_pure=is_pure,
            is_deterministic=is_deterministic,
            parameters=parameters,
            return_type=return_type,
            side_effects=side_effects,
            dependencies=dependencies,
            source_location=source_location,
        )

    def extract_from_javascript_function(
        self,
        func: JSFunction,
        source_file: Optional[str] = None,
    ) -> IntentUnit:
        """
        Extract intent unit from a JavaScript function.
        
        Args:
            func: The parsed JavaScript function
            source_file: Optional source file path
            
        Returns:
            IntentUnit: The extracted intent unit
        """
        jsdoc_text = func.jsdoc or ""
        intent = self._classify_intent(
            func.name,
            jsdoc_text,
            set(p.name for p in func.parameters),
        )

        is_pure = func.purity == JSPurity.PURE
        is_deterministic = is_pure

        parameters = [
            {
                "name": p.name,
                "type": None,  # JS doesn't have type annotations in plain JS
                "optional": p.has_default,
                "default": p.default_value,
            }
            for p in func.parameters
        ]

        side_effects = [se.value for se in func.side_effects if se.value != "none"]

        dependencies = list(func.external_calls)

        source_location = {"file": source_file} if source_file else None

        return IntentUnit(
            source=func.source,
            language="javascript",
            function_name=func.name,
            intent=intent,
            is_pure=is_pure,
            is_deterministic=is_deterministic,
            parameters=parameters,
            return_type=None,
            side_effects=side_effects,
            dependencies=dependencies,
            source_location=source_location,
        )

    def extract_from_python_class(
        self,
        cls: PythonClass,
        source_file: Optional[str] = None,
    ) -> List[IntentUnit]:
        """
        Extract intent units from a Python class.
        
        Each public method becomes a separate intent unit.
        
        Args:
            cls: The parsed Python class
            source_file: Optional source file path
            
        Returns:
            List of IntentUnits
        """
        units = []

        for method in cls.methods:
            if method.name.startswith('_') and method.name != '__init__':
                continue

            unit = self.extract_from_python_function(method, source_file)
            units.append(unit)

        return units

    def _classify_intent(
        self,
        name: str,
        docstring: str,
        param_names: Set[str],
    ) -> AtomicIntent:
        """Classify the intent of a function based on its characteristics."""
        name_lower = name.lower()
        doc_lower = docstring.lower()
        combined_text = f"{name_lower} {doc_lower} {' '.join(param_names)}"

        category = self._detect_category(name_lower, combined_text)
        atomicity = self._assess_atomicity(name_lower, len(param_names), docstring)
        keywords = self._extract_keywords(name_lower, doc_lower)
        description = self._generate_description(name, category, docstring)

        intent_id = self._generate_intent_id(name, category)
        semantic_signature = hashlib.sha256(
            f"{name}:{category.value}:{','.join(sorted(keywords))}".encode()
        ).hexdigest()[:16]

        return AtomicIntent(
            intent_id=intent_id,
            name=name,
            description=description,
            category=category,
            atomicity=atomicity,
            keywords=tuple(sorted(keywords)),
            semantic_signature=semantic_signature,
        )

    def _detect_category(self, name: str, combined_text: str) -> IntentCategory:
        """Detect the intent category from function characteristics."""
        category_keywords = [
            (IntentCategory.ARITHMETIC, self.ARITHMETIC_KEYWORDS),
            (IntentCategory.STRING_MANIPULATION, self.STRING_KEYWORDS),
            (IntentCategory.LIST_OPERATION, self.LIST_KEYWORDS),
            (IntentCategory.COMPARISON, self.COMPARISON_KEYWORDS),
            (IntentCategory.VALIDATION, self.VALIDATION_KEYWORDS),
            (IntentCategory.TRANSFORMATION, self.TRANSFORMATION_KEYWORDS),
            (IntentCategory.AGGREGATION, self.AGGREGATION_KEYWORDS),
            (IntentCategory.FILTERING, self.FILTER_KEYWORDS),
            (IntentCategory.SORTING, self.SORT_KEYWORDS),
        ]

        best_category = IntentCategory.UNKNOWN
        best_score = 0

        for category, keywords in category_keywords:
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > best_score:
                best_score = score
                best_category = category

        return best_category

    def _assess_atomicity(
        self,
        name: str,
        param_count: int,
        docstring: str,
    ) -> AtomicityLevel:
        """Assess how atomic a function is."""
        if param_count <= 2 and len(name) < 20:
            return AtomicityLevel.ATOMIC

        if "and" in name.lower() or "or" in name.lower():
            return AtomicityLevel.COMPOSITE

        if param_count > 5:
            return AtomicityLevel.COMPLEX

        return AtomicityLevel.ATOMIC

    def _extract_keywords(self, name: str, docstring: str) -> Set[str]:
        """Extract relevant keywords from function name and docstring."""
        keywords: Set[str] = set()

        words = set(name.replace('_', ' ').split())
        keywords.update(words)

        all_keywords = (
            self.ARITHMETIC_KEYWORDS |
            self.STRING_KEYWORDS |
            self.LIST_KEYWORDS |
            self.COMPARISON_KEYWORDS |
            self.VALIDATION_KEYWORDS |
            self.TRANSFORMATION_KEYWORDS |
            self.AGGREGATION_KEYWORDS |
            self.FILTER_KEYWORDS |
            self.SORT_KEYWORDS
        )

        for kw in all_keywords:
            if kw in name or kw in docstring:
                keywords.add(kw)

        return keywords

    def _generate_description(
        self,
        name: str,
        category: IntentCategory,
        docstring: str,
    ) -> str:
        """Generate a description for the intent."""
        if docstring and docstring.strip():
            first_line = docstring.strip().split('\n')[0]
            return first_line[:200]

        readable_name = name.replace('_', ' ').title()
        return f"{readable_name} ({category.value})"

    def _generate_intent_id(self, name: str, category: IntentCategory) -> str:
        """Generate a unique intent ID."""
        self._intent_counter += 1
        base = f"{category.value}:{name}"
        return f"intent:{hashlib.sha256(base.encode()).hexdigest()[:12]}"
