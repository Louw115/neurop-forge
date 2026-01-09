"""
Intent classifier for categorizing code units.

This module provides advanced intent classification using:
- Semantic analysis of function names
- Docstring analysis
- Parameter and return type analysis
- Code pattern recognition

The classifier ensures that intent is derived from AST evidence,
never from guessing.
"""

import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from neurop_forge.parsing.intent_units import IntentUnit, IntentCategory, AtomicityLevel


class ConfidenceLevel(Enum):
    """Confidence level of classification."""
    HIGH = "high"  # >= 0.8
    MEDIUM = "medium"  # >= 0.5
    LOW = "low"  # >= 0.3
    UNCERTAIN = "uncertain"  # < 0.3


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    intent_unit: IntentUnit
    primary_category: IntentCategory
    secondary_categories: Tuple[IntentCategory, ...]
    confidence: float
    confidence_level: ConfidenceLevel
    classification_evidence: Dict[str, Any]
    is_atomic: bool
    requires_decomposition: bool
    semantic_tags: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_category": self.primary_category.value,
            "secondary_categories": [c.value for c in self.secondary_categories],
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "classification_evidence": self.classification_evidence,
            "is_atomic": self.is_atomic,
            "requires_decomposition": self.requires_decomposition,
            "semantic_tags": list(self.semantic_tags),
        }

    def is_valid_for_block(self) -> bool:
        """Check if this classification is valid for block creation."""
        return (
            self.confidence >= 0.3 and
            self.is_atomic and
            not self.requires_decomposition
        )


class IntentClassifier:
    """
    Advanced intent classifier using AST evidence.
    
    Classification is based on:
    1. Function name patterns
    2. Parameter signatures
    3. Return type information
    4. Docstring analysis
    5. Code structure patterns
    
    No guessing is allowed - all classifications must have evidence.
    """

    CATEGORY_PATTERNS: Dict[IntentCategory, List[Tuple[str, float]]] = {
        IntentCategory.ARITHMETIC: [
            (r'^add[_\s]|_add$|^sum[_\s]|^plus', 0.9),
            (r'^sub(tract)?[_\s]|^minus|^diff', 0.9),
            (r'^mult(iply)?[_\s]|^product', 0.9),
            (r'^div(ide)?[_\s]|^quotient', 0.9),
            (r'^pow(er)?[_\s]|^exp|^sqrt|^square', 0.9),
            (r'^abs[_\s]|^absolute', 0.85),
            (r'^mod(ulo)?[_\s]|^remainder', 0.85),
            (r'^floor|^ceil|^round', 0.85),
            (r'^min[_\s]|^max[_\s]|^clamp', 0.85),
            (r'^avg|^average|^mean|^median', 0.9),
            (r'^calculate|^compute|^eval', 0.7),
        ],
        IntentCategory.STRING_MANIPULATION: [
            (r'^concat|^join|^merge.*str', 0.9),
            (r'^split|^tokenize|^parse.*str', 0.9),
            (r'^trim|^strip|^clean', 0.85),
            (r'^upper|^lower|^capitalize|^title', 0.9),
            (r'^replace|^substitute|^swap', 0.8),
            (r'^format|^template|^interpolate', 0.85),
            (r'^pad|^justify|^align', 0.85),
            (r'^encode|^decode|^escape|^unescape', 0.85),
            (r'^substr|^substring|^slice.*str', 0.85),
        ],
        IntentCategory.LIST_OPERATION: [
            (r'^append|^push|^add.*list|^add.*array', 0.9),
            (r'^pop|^shift|^remove.*list', 0.9),
            (r'^insert|^splice', 0.85),
            (r'^flatten|^nest|^unnest', 0.9),
            (r'^unique|^distinct|^dedupe', 0.9),
            (r'^chunk|^partition|^batch', 0.9),
            (r'^reverse.*list|^rotate', 0.85),
            (r'^zip|^unzip|^transpose', 0.9),
        ],
        IntentCategory.COMPARISON: [
            (r'^compare|^cmp|^diff', 0.9),
            (r'^equal|^eq[_\s]|^same', 0.9),
            (r'^greater|^gt[_\s]|^more', 0.85),
            (r'^less|^lt[_\s]|^fewer', 0.85),
            (r'^between|^in_range|^within', 0.9),
            (r'^match|^matches', 0.8),
        ],
        IntentCategory.VALIDATION: [
            (r'^is_|^has_|^can_|^should_', 0.9),
            (r'^validate|^check|^verify', 0.9),
            (r'^assert|^ensure|^require', 0.85),
            (r'^test[_\s]|^confirm', 0.7),
        ],
        IntentCategory.TRANSFORMATION: [
            (r'^to_|^as_|^into_', 0.9),
            (r'^from_|^parse_', 0.85),
            (r'^convert|^transform|^map(?!ping)', 0.9),
            (r'^serialize|^deserialize', 0.9),
            (r'^marshal|^unmarshal', 0.9),
        ],
        IntentCategory.AGGREGATION: [
            (r'^sum[_\s]|^total|^count', 0.9),
            (r'^reduce|^fold|^accumulate', 0.9),
            (r'^aggregate|^combine|^collect', 0.9),
            (r'^group|^cluster|^bucket', 0.85),
        ],
        IntentCategory.FILTERING: [
            (r'^filter|^select|^where', 0.9),
            (r'^find|^search|^query', 0.85),
            (r'^get|^fetch|^lookup', 0.7),
            (r'^pick|^pluck|^extract', 0.85),
            (r'^reject|^exclude|^omit', 0.9),
        ],
        IntentCategory.SORTING: [
            (r'^sort|^order|^rank', 0.9),
            (r'^arrange|^organize', 0.8),
            (r'^shuffle|^randomize', 0.85),
        ],
        IntentCategory.SEARCHING: [
            (r'^search|^find|^locate', 0.85),
            (r'^index_of|^position', 0.9),
            (r'^contains|^includes|^has', 0.8),
            (r'^starts_with|^ends_with', 0.9),
        ],
    }

    ATOMIC_INDICATORS: Set[str] = {
        "single", "one", "simple", "basic", "pure",
        "atomic", "primitive", "elementary",
    }

    COMPOSITE_INDICATORS: Set[str] = {
        "and", "then", "also", "with", "including",
        "multiple", "batch", "bulk", "many",
    }

    def __init__(self):
        self._compiled_patterns: Dict[IntentCategory, List[Tuple[re.Pattern, float]]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        for category, patterns in self.CATEGORY_PATTERNS.items():
            self._compiled_patterns[category] = [
                (re.compile(pattern, re.IGNORECASE), weight)
                for pattern, weight in patterns
            ]

    def classify(self, intent_unit: IntentUnit) -> ClassificationResult:
        """
        Classify an intent unit into categories.
        
        Args:
            intent_unit: The intent unit to classify
            
        Returns:
            ClassificationResult with classification details
        """
        name = intent_unit.function_name
        docstring = intent_unit.intent.description
        param_names = [p.get("name", "") for p in intent_unit.parameters]
        return_type = intent_unit.return_type or ""

        category_scores: Dict[IntentCategory, float] = {}
        evidence: Dict[str, Any] = {
            "name_matches": [],
            "docstring_matches": [],
            "param_matches": [],
            "return_type_evidence": None,
        }

        for category, patterns in self._compiled_patterns.items():
            score = 0.0
            for pattern, weight in patterns:
                if pattern.search(name):
                    score = max(score, weight)
                    evidence["name_matches"].append({
                        "pattern": pattern.pattern,
                        "category": category.value,
                        "weight": weight,
                    })

                if pattern.search(docstring):
                    doc_weight = weight * 0.7
                    score = max(score, doc_weight)
                    evidence["docstring_matches"].append({
                        "pattern": pattern.pattern,
                        "category": category.value,
                        "weight": doc_weight,
                    })

            if score > 0:
                category_scores[category] = score

        return_type_category = self._infer_from_return_type(return_type)
        if return_type_category:
            current = category_scores.get(return_type_category, 0)
            category_scores[return_type_category] = max(current, 0.6)
            evidence["return_type_evidence"] = {
                "return_type": return_type,
                "inferred_category": return_type_category.value,
            }

        if not category_scores:
            category_scores[IntentCategory.UTILITY] = 0.3

        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        primary_category = sorted_categories[0][0]
        primary_score = sorted_categories[0][1]
        secondary_categories = tuple(cat for cat, _ in sorted_categories[1:4])

        confidence_level = self._determine_confidence_level(primary_score)

        is_atomic = self._check_atomicity(name, docstring, len(intent_unit.parameters))
        requires_decomposition = not is_atomic or len(intent_unit.parameters) > 5

        semantic_tags = self._extract_semantic_tags(
            name, docstring, primary_category, param_names
        )

        return ClassificationResult(
            intent_unit=intent_unit,
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence=primary_score,
            confidence_level=confidence_level,
            classification_evidence=evidence,
            is_atomic=is_atomic,
            requires_decomposition=requires_decomposition,
            semantic_tags=semantic_tags,
        )

    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score."""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN

    def _infer_from_return_type(self, return_type: str) -> Optional[IntentCategory]:
        """Infer category from return type."""
        rt = return_type.lower()

        if rt in ("int", "float", "decimal", "number"):
            return IntentCategory.ARITHMETIC
        elif rt in ("str", "string", "text"):
            return IntentCategory.STRING_MANIPULATION
        elif "list" in rt or "array" in rt or "sequence" in rt:
            return IntentCategory.LIST_OPERATION
        elif rt in ("bool", "boolean"):
            return IntentCategory.VALIDATION
        elif "dict" in rt or "map" in rt:
            return IntentCategory.DICT_OPERATION

        return None

    def _check_atomicity(
        self,
        name: str,
        docstring: str,
        param_count: int,
    ) -> bool:
        """Check if the function represents an atomic intent."""
        name_lower = name.lower()
        doc_lower = docstring.lower()
        combined = f"{name_lower} {doc_lower}"

        for indicator in self.COMPOSITE_INDICATORS:
            if f"_{indicator}_" in name_lower or f" {indicator} " in doc_lower:
                return False

        if param_count > 5:
            return False

        if "_and_" in name_lower or "_or_" in name_lower:
            return False

        return True

    def _extract_semantic_tags(
        self,
        name: str,
        docstring: str,
        category: IntentCategory,
        param_names: List[str],
    ) -> Tuple[str, ...]:
        """Extract semantic tags for the intent."""
        tags: Set[str] = set()

        tags.add(category.value)

        words = set(name.lower().replace('_', ' ').split())
        tags.update(w for w in words if len(w) > 2)

        for param in param_names:
            if param not in ('self', 'cls', 'args', 'kwargs'):
                tags.add(param.lower())

        return tuple(sorted(tags))

    def batch_classify(
        self,
        intent_units: List[IntentUnit],
    ) -> List[ClassificationResult]:
        """
        Classify multiple intent units.
        
        Args:
            intent_units: List of intent units to classify
            
        Returns:
            List of classification results
        """
        return [self.classify(unit) for unit in intent_units]
